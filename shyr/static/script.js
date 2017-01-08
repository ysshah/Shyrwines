$(document).ready(function () {

    /* Autocomplete function. */
    $("#nav-search").keyup(function () {
        if ($("#nav-search").val()) {
            $.ajax({
                url: "/autocomplete/",
                type: "GET",
                data: $(this).parent().serialize(),
                success: function(data) {
                    if (data) {
                        $("#auto-container").html(data);
                        $("#auto-container").show();
                    } else {
                        $("#auto-container").hide();
                    }
                }
            });
        } else {
            $("#auto-container").hide();
        }
    });

    /* Adds a wine to the cart from the VIEW page. */
    $('#nav-cart').popover({
        trigger: 'manual',
        content: ' '
    });
    $('form#add').submit(function(e) {
        e.preventDefault();
        var name = $(this).children('input[name=name]').val();
        var quantity = $(this).children('input[name=quantity]').val();
        $.post('/add/', $(this).serialize(), function(data) {
            var message = name + ' (' + quantity + ') added to cart.';
            if ($(window).width() < 768) {
                $('#add-modal').find('.modal-body').text(message);
                $('#add-modal').modal('show');
            } else {
                var popover = $('#nav-cart').data('bs.popover');
                popover.config.content = message;
                $('#nav-cart').popover('show');
                setTimeout(function() {
                    $('#nav-cart').popover('hide');
                }, 2000);
            }
        });
    });

    /* Update a wine's quantity in the cart upon its quantity change. */
    $(document).on('change', 'input.cart-quantity', function() {
        $.post('/update/', $(this).parent().serialize(), function(data) {
            $('div.cart-wrapper').load('/cart-items/');
        });
    });

    /* Remove a wine bottle from the cart. */
    $(document).on('submit', 'form.remove', function(e) {
        e.preventDefault();
        $.post('/remove/', $(this).serialize(), function(data) {
            $('div.cart-wrapper').load('/cart-items/');
        });
    });

    /* Validate order form upon "Submit Order" button click. */
    $('form#order').submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: '/checkout/',
            type: "GET",
            data: $(this).serialize(),
            success: function(msg) {
                if (msg) {
                    alert(msg);
                } else {
                    $('#thanks-modal').modal({
                        backdrop: 'static',
                        keyboard: false
                    });
                }
            }
        });
    });

});
