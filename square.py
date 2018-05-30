import os
import pandas as pd
import requests


BASE_DIR = os.path.expanduser('~/Dropbox/Shyr/')
EXCEL_FILE = BASE_DIR + 'ShyrWineList.xlsx'

ACCESS_TOKEN = ''
REQUEST_HEADERS = {
    'Authorization': 'Bearer ' + ACCESS_TOKEN,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}
LOCATION_ID = ''
TAX_FEE_ID = ''


def readExcel():
    """Read an Excel file into a Pandas DataFrame object."""
    df = pd.read_excel(EXCEL_FILE)

    # Remove No-Adv wines and unnecessary columns
    df = df.loc[df['No-Adv'] != 'N']
    df.drop(['Cost', 'Margin', 'Rev Margin', 'No-Adv'], axis=1, inplace=True)

    # Convert price to integer to avoid floating point errors
    df['Price'] = df['Price'].apply(lambda x: round(x * 100))

    # TODO: Validate Excel file
    # if df[REQUIRED_FIELDS].isnull().any().any():
    #     for i in df.index[df[REQUIRED_FIELDS].isnull().any(axis=1)]:
    #         print('Error: Row {} is missing {}'.format(
    #             i, REQUIRED_FIELDS[np.where(df.loc[i,REQUIRED_FIELDS].isnull())[0]]))
    #     sys.exit(1)

    return df


def squareRequest(url, method='get', image=False, **kwargs):
    """Send a METHOD request to Square with URL suffix.

    If IMAGE is True, then drop the 'Content-Type: application/json' from the
    request headers. KWARGS can be data, files, etc.
    """
    headers = REQUEST_HEADERS.copy()
    if image:
        headers.pop('Content-Type')

    baseURL = 'https://connect.squareup.com/v1/'
    if method == 'get':
        req = requests.get
    elif method == 'put':
        req = requests.put
    elif method == 'post':
        req = requests.post

    r = req(baseURL + url, headers=headers, **kwargs)
    if r.status_code != 200:
        raise RuntimeError(r.text)
    return r

def locationRequest(url, **kwargs):
    """Prepend LOCATION_ID to URL and send request."""
    return squareRequest(LOCATION_ID + url, **kwargs)

def inventoryRequest(url='', **kwargs):
    """Prepend {LOCATION_ID}/inventory to URL and send request."""
    return locationRequest('/inventory' + url, **kwargs)

def itemRequest(url='', **kwargs):
    """Prepend {LOCATION_ID}/items to URL and send request."""
    return locationRequest('/items' + url, **kwargs)

def variationRequest(item_id, variation_id, **kwargs):
    """Send request {LOCATION_ID}/items/{ITEM_ID}/variations/{VARIATION_ID}."""
    return itemRequest('/{}/variations/{}'.format(item_id, variation_id), **kwargs)


def getLocationID():
    """Retrieve first Square location ID."""
    return squareRequest('me/locations').json()[0]['id']


def getSquareItems():
    """Return all Square items as Pandas DataFrame. Append variation columns
    variation_id, SKU, price, track_inventory, and quantity_on_hand.
    """
    print('Retrieving items from Square...')

    r = itemRequest()
    df_items = pd.read_json(r.text).fillna('')
    df_items = df_items[['id', 'name', 'description', 'master_image']]

    df_variations = pd.io.json.json_normalize([j['variations'][0] for j in r.json()])
    df_variations = df_variations.rename(columns={
        'price_money.amount':'price', 'id':'variation_id'}
        )[['item_id', 'sku', 'price', 'variation_id', 'track_inventory']]
    df_variations['sku'] = df_variations['sku'].astype(int)

    df_inventory = pd.read_json(inventoryRequest().text)

    return df_items.merge(df_variations.merge(df_inventory),
        left_on='id', right_on='item_id').drop('id', axis=1)


def syncImagesWithSquare(sync=True):
    df = getSquareItems()
    print('Out of {} total wines, {} missing pictures in Square.'.format(len(df), np.sum(df.master_image == '')))

    if sync:
        for _, wine in df[df.master_image == ''].iterrows():
            image = IMAGE_PATH.format(wine.sku)
            if os.path.isfile(image):
                files = [('image_data', (image, open(image, 'rb'), 'image/jpeg'))]
                out('Uploading image for SKU {}: {}...'.format(wine.sku, wine['name']))
                itemRequest('/{}/image'.format(wine.item_id), method='post', image=True, files=files)
                out(' Done.\n')


def add1000ToStock(variation_id):
    data = json.dumps({
        'quantity_delta': 1000,
        'adjustment_type': 'RECEIVE_STOCK'
    })
    inventoryRequest('/' + variation_id, method='post', data=data)


def updateSquareWineInventory(old, new):
    if old.track_inventory:
        if new.Count == 0 and old.quantity_on_hand > 0:
            print('\nUpdate SKU {}: {}'.format(new.SKU, new['name']))
            printUpdateString('count', old.quantity_on_hand, 0)
            data = json.dumps({
                'quantity_delta': int(-old.quantity_on_hand),
                'adjustment_type': 'SALE'
            })
            inventoryRequest('/' + old.variation_id,
                method='post', data=data)
            return 1
        elif new.Count > 0 and old.quantity_on_hand == 0:
            print('\nUpdate SKU {}: {}'.format(new.SKU, new['name']))
            printUpdateString('count', old.quantity_on_hand, 1000)
            add1000ToStock(old.variation_id)
            return 1
        return 0
    else:
        print('Add inventory tracking to', new.Name)
        variationRequest(old.item_id, old.variation_id, method='put',
            data=json.dumps({'track_inventory': True}))
        if new.Count > 0:
            add1000ToStock(old.variation_id)
        return 1


def updateSquareWineInfo(old, new, columns):
    if 'price' in columns:
        columns.remove('price')
        printUpdateString('price', old.price, new.price)
        data = json.dumps({
            'price_money': {
                'currency_code': 'USD',
                'amount': new.price
            }
        })
        variationRequest(old.item_id, old.variation_id, method='put', data=data)
    if len(columns) > 0:
        for column in columns:
            printUpdateString(column, old[column], new[column])
        itemRequest('/' + old.item_id, method='put', data=json.dumps(dict(new[columns])))


def addWineToSquare(new):
    """Insert new wine into Square database.

    NEW is a Pandas Series of the new wine. First post the item, then add tax,
    then add inventory if wine's count is not 0.
    """
    data = json.dumps({
        'name': new['name'],
        'description': new.description,
        'variations': [{
            'price_money': {
                'currency_code': 'USD',
                'amount': new.price
            },
            'sku': str(new.SKU),
            'track_inventory': True
        }]
    })
    item = itemRequest(method='post', data=data)
    item_id = item.json()['id']
    itemRequest('/{}/fees/{}'.format(item_id, TAX_FEE_ID), method='put')
    if new.Count > 0:
        add1000ToStock(item.json()['variations'][0]['id'])


def syncWinesWithSquare(sync=True):
    """Sync the Excel spreadsheet with Square database."""
    init()
    new_df = readExcel(EXCEL_FILE).fillna('').rename(columns={'Name':'name',
        'Description':'description', 'Price':'price'})
    old_df = getSquareItems()

    print('Analyzing differences...')
    columns = np.array(['name', 'description', 'price'])
    numInserts, numUpdates = 0, 0
    for i, new in new_df.iterrows():
        if new.SKU in old_df['sku'].values:
            old = old_df[old_df['sku'] == new.SKU].iloc[0]
            numUpdates += updateSquareWineInventory(old, new)
            columnsAreDifferent = np.array(old[columns] != new[columns], dtype=bool)
            differentColumns = columns[columnsAreDifferent].tolist()
            if len(differentColumns) > 0:
                numUpdates += 1
                print('\nUpdate SKU {}: {}'.format(new.SKU, new['name']))
                updateSquareWineInfo(old, new, differentColumns)
        else:
            numInserts += 1
            print('Insert SKU {}: {}'.format(new.SKU, new['name']))
            if sync:
                addWineToSquare(new)

    if numInserts + numUpdates == 0:
        print('No differences.')
    else:
        print('\n{} updates, {} inserts.'.format(numUpdates, numInserts))
