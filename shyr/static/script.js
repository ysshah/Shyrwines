$(document).ready(function () {

    /* Autocomplete function. */
    $("#nav-search").keyup(function () {
        if ($("#nav-search").val()) {
            $.ajax({
                url: "/autocomplete/",
                type: "GET",
                data: $("form.search").serialize(),
                success: function (data) {
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
    $('form.add').submit(function(e) {
        e.preventDefault();
        var name = $(this).children('input[name=name]').val();
        var quantity = $(this).children('input[name=quantity]').val();
        $.post('/add/', $(this).serialize(), function(data) {
            if ($(window).width() < 768) {
                $("div#dimmer").fadeIn(function () {
                    $("div#popover-content").fadeIn().delay(1000).fadeOut(function () {
                        $("div#dimmer").fadeOut();
                    });
                });
            } else {
                var popover = $('#nav-cart').data('bs.popover');
                popover.config.content = name + ' (' + quantity + ') added to cart.';
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

    // /* Validate an email address. */
    // function validate_email(passed) {
    //     var email = $("input#email");
    //     var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    //     if (!email.val()) {
    //         email.css("border-color", "red");
    //         email.parent().css("color", "red");
    //         email.attr("placeholder", "Required");
    //         return false;
    //     } else if (!regex.test(email.val())) {
    //         $("div#form-email label").text("Invalid email address.");
    //         email.css("border-color", "red");
    //         email.parent().css("color", "red");
    //         return false;
    //     } else {
    //         $("div#form-email label").text("Email");
    //         email.parent().css("color", "black");
    //         email.css("border-color", "rgba(142, 6, 6, 0.5)");
    //         return passed;
    //     }
    // }

    // /* Validate a zipcode. Either 55555 or 55555-5555. */
    // function validate_zipcode(passed) {
    //     var zipcode = $("input#zipcode");
    //     if (!zipcode.val()) {
    //         zipcode.css("border-color", "red");
    //         zipcode.parent().css("color", "red");
    //         zipcode.attr("placeholder", "Required");
    //         return false;
    //     } else if (!/^\d{5}(-\d{4})?$/.test(zipcode.val())) {
    //         $("div#form-zipcode label").text("Invalid zip.");
    //         zipcode.css("border-color", "red");
    //         zipcode.parent().css("color", "red");
    //         return false;
    //     } else {
    //         $("div#form-zipcode label").text("Zip Code");
    //         zipcode.parent().css("color", "black");
    //         zipcode.css("border-color", "rgba(142, 6, 6, 0.5)");
    //         return passed;
    //     }
    // }

    // /* Validate the order form on the cart page. */
    // function validate() {
    //     var passed = true;
    //     $("input.order-form:not(input#email, input#zipcode),"
    //         + "select#state").each(function () {
    //         if (!$(this).val()) {
    //             $(this).css("border-color", "red");
    //             $(this).parent().css("color", "red");
    //             $(this).attr("placeholder", "Required");
    //             passed = false;
    //         }
    //     });
    //     if (!$("input#agree").prop("checked")) {
    //         $("div#form-agree label").css("color", "red");
    //         passed = false;
    //     }
    //     passed = validate_email(passed);
    //     passed = validate_zipcode(passed);
    //     return passed;
    // }

    // /* Change the agreement text to red or black depending on agreement. */
    // $("input#agree").change(function () {
    //     if (!$(this).prop("checked")) {
    //         $("div#form-agree label").css("color", "red");
    //     } else {
    //         $("div#form-agree label").css("color", "black");
    //     }
    // });

    // /* Validate input fields upon focusout. */
    // $("input.order-form:not(input#email, input#zipcode),"
    //     + "select#state").focusout(function () {
    //     if ($(this).val()) {
    //         $(this).parent().css("color", "black");
    //         $(this).css("border-color", "rgba(142, 6, 6, 0.5)");
    //     } else {
    //         $(this).css("border-color", "red");
    //         $(this).parent().css("color", "red");
    //         $(this).attr("placeholder", "Required");
    //     }
    // });

    // /* Validate email upon focusout. */
    // $("input#email").focusout(function () {
    //     validate_email(true);
    // });

    // /* Validate zipcode upon focusout. */
    // $("input#zipcode").focusout(function () {
    //     validate_zipcode(true);
    // });

    // /* Validate order form upon "Submit Order" button click. */
    // $("button#submit-order").click(function () {
    //     if (validate()) {
    //         $.ajax({
    //             url: '/checkout/',
    //             type: "GET",
    //             data: $("#order-form").serialize(),
    //             success: function(msg) {
    //                 if (msg) {
    //                     alert(msg);
    //                 } else {
    //                     $("div#cart-content").slideUp();
    //                     $("form#order-form").slideUp(function () {
    //                         $("div#dimmer").fadeIn(function () {
    //                             $("div#thanks-wrapper").fadeIn();
    //                         });
    //                     });
    //                 }
    //             }
    //         });
    //     }
    // });

});
