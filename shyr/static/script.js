$(document).ready(function () {

    /* Autocomplete function. */
    $("#nav-search").keyup(function () {
        if ($("#nav-search").val()) {
            $.get('/autocomplete/', $(this).parent().serialize(),
                function(data) {
                    if (data) {
                        $("#auto-container").html(data);
                        $("#auto-container").show();
                    } else {
                        $("#auto-container").hide();
                    }
                }
            );
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
        $.get('/add/', $(this).serialize(), function(data) {
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
        $.get('/update/', $(this).parent().serialize(), function(data) {
            $('div.cart-wrapper').html(data);
        });
    });

    /* Remove a wine bottle from the cart. */
    $(document).on('submit', 'form.remove', function(e) {
        e.preventDefault();
        $.get('/remove/', $(this).serialize(), function(data) {
            $('div.cart-wrapper').html(data);
        });
    });

    $('form#order').validate({
        errorPlacement: function(error, element) {
            $(element).attr('placeholder', 'Required');
        },
        highlight: function(element, errorClass, validClass) {
            if ($(element).attr('type') == 'checkbox') {
                $(element).parent().parent().addClass('has-danger');
            } else {
                $(element).parent().addClass('has-danger');
            }
        },
        unhighlight: function(element, errorClass, validClass) {
            if ($(element).attr('type') == 'checkbox') {
                $(element).parent().parent().removeClass('has-danger');
            } else {
                $(element).parent().removeClass('has-danger');
            }
        },
        submitHandler: function(form) {
            $.get('/checkout/', $(form).serialize(), function(msg) {
                if (msg) {
                    alert(msg);
                } else {
                    $('#thanks-modal').modal({
                        backdrop: 'static',
                        keyboard: false
                    });
                }
            });
        }
    });
    /* Validate order form upon "Submit Order" button click. */
    // $('form#order').submit(function(e) {
    //     e.preventDefault();
    //     $.ajax({
    //         url: '/checkout/',
    //         type: "GET",
    //         data: $(this).serialize(),
    //         success: function(msg) {
    //             if (msg) {
    //                 alert(msg);
    //             } else {
    //                 $('#thanks-modal').modal({
    //                     backdrop: 'static',
    //                     keyboard: false
    //                 });
    //             }
    //         }
    //     });
    // });

});
