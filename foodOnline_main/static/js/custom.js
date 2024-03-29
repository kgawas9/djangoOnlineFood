let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['in']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        // console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields

    // console.log(place)
    
    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value

    // console.log(address)
    geocoder.geocode({'address': address}, function(results, status){
        // console.log('results =>', results)
        // console.log('status =>', status)

        if(status == google.maps.GeocoderStatus.OK){
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();
        }
        // console.log(latitude);
        // console.log(longitude);
        
        $('#id_latitude').val(latitude);
        $('#id_longitude').val(longitude);

        $('#id_address').val(address); 
    });

    // loop through the address components and assign other data
    // console.log(place.address_components)

    for(var i=0; i<place.address_components.length; i++){
        for(var j=0; j<place.address_components[i].types.length; j++){
            // get country
            if (place.address_components[i].types[j] == 'country'){
                $('#id_country').val(place.address_components[i].long_name);
            }

            if (place.address_components[i].types[j] == 'administrative_area_level_1'){
                $('#id_state').val(place.address_components[i].long_name);
            }

            if (place.address_components[i].types[j] == 'administrative_area_level_2'){
                $('#id_city').val(place.address_components[i].long_name);
            }

            // if postal code is not available
            if (place.address_components[i].types[j] == 'postal_code'){
                $('#id_pin_code').val(place.address_components[i].long_name);
            }else{
                $('#id_pin_code').val("");
            }
            
        }
    }
}


// To refresh the page on back button

window.addEventListener( "pageshow", function ( event ) {
    var historyTraversal = event.persisted;
    if ( historyTraversal ) {
      // Handle page restore.
      if (this.window.location.href.indexOf("marketplace") > -1){
            window.location.reload();
      }
    }
  });

//   ( typeof window.performance != "undefined" && 
//   window.performance.getEntriesByType("navigation")[2].type );

$(document).ready(function(){
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();
        
        // get food id 
        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        data = {
            food_id: food_id,
        }

        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: function(response){
                // alert(response);    // response from add_to_cart view (HttpResponse)
                // console.log(response);
                if (response.status == 'login_required'){
                    swal(
                        response.message, '', 'info'
                    ).then(function(){
                        window.location = '/login';
                    })
                }if (response.status == 'failed'){
                    swal(
                        response.message, '', 'error'
                    )
                }
                else{
                    $('#qty-'+food_id).html(response.qty);
                    $('#cart_counter').html(response.cart_counter['cart_count']);

                    // subtotal, tax and total
                    // console.log(response)
                    // console.log(response.cart_amount['subtotal'])

                    cart_amounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['total'],
                    )
                }
            }
        });
    })

    // place the cart item quantity on load
    $('.item_qty').each(function(){
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        
        $('#'+the_id).html(qty);
    })


    // To decrease cart item functionality

    $('.decrease_cart').on('click', function(e){
        e.preventDefault();

        // get food id and triggered url
        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        cart_id = $(this).attr('id');

        // console.log(food_id);
        // console.log(url);

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response);
                if (response.status == 'login_required'){
                    swal(
                        response.message, '', 'info'
                    ).then(function(){
                        window.location = '/login/';
                    })
                }if (response.status == 'failed'){
                    swal(
                        response.message, '', 'error'
                    )
                }
                else{
                    
                    
                    $('#qty-'+food_id).html(response.qty);
                    
                    if(response.qty == 0){
                        if (window.location.pathname == '/cart/'){
                            remove_cart_item(response.qty, cart_id);
                        }
                    }

                    $('#cart_counter').html(response.cart_counter['cart_count']);

                    // Check for use is available in cart page or not.. else it throws javascript error
                    if (window.location.pathname == '/cart/'){
                        check_for_empty_cart();
                    }

                    cart_amounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['total'],
                    )
                }   
            }
        })

    })

    // For delete cart item functionality

    $('.delete_cart').on('click', function(e){
        e.preventDefault();

        // get food id and triggered url
        cart_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        // console.log(food_id);
        // console.log(url);

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response);
                if (response.status == 'login_required'){
                    swal(
                        'title', 'subtitle', 'info'
                    )
                }if (response.status == 'failed'){
                    swal(
                        response.status, response.message, 'error'
                    )
                }
                else{
                    // call function to remove the item from cart
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    remove_cart_item(0, cart_id)

                    // if cart is empty then show the empty messge
                    check_for_empty_cart();
                    swal(
                        response.status, response.message, 'success'
                    )

                    cart_amounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['total'],
                    )
                }   
            }
        })

    })

    // delete cart element if the quantity is 0
    function remove_cart_item(cart_item_qty, cart_id){
        if(cart_item_qty <= 0){
            // remove cart item element
            document.getElementById("cart-item-"+cart_id).remove();
        }
    }

    function check_for_empty_cart(){
        var cart_counter = document.getElementById('cart_counter').innerHTML
        if(cart_counter == 0){
            document.getElementById('empty-cart').style.display = "block";
        }
    }

    // function to read cart amounts

    function cart_amounts(subtotal, tax_dict, total){
        if (window.location.pathname == '/cart/'){
            $('#subtotal').html(subtotal);
            // $('#tax').html(tax);
            $('#total').html(total);

            for(key1 in tax_dict){
                console.log(tax_dict[key1])
                for(key2 in tax_dict[key1]){
                    // console.log(tax_dict[key1][key2])
                    $('#tax-'+key1).html(tax_dict[key1][key2])
                }
            }
        }
    }

    // add opening hours
    $('.add_hour').on('click', function(e){
        e.preventDefault();

        var day = document.getElementById('id_day').value;
        var from_hour = document.getElementById('id_from_hour').value;
        var to_hour = document.getElementById('id_to_hour').value;
        var is_closed = document.getElementById('id_is_closed').checked;
        // jquery syntax
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var url = document.getElementById('add_hour_url').value;


        // console.log(day, from_hour, to_hour, is_closed, csrf_token);

        if(is_closed){
            is_closed = 'True';
            condition = "day!= ''"
        }else{
            is_closed = "False";
            condition = "day!= '' && from_hour != '' && to_hour != ''"
        }

        if(eval(condition)){
            $.ajax({
                type: 'POST',
                url: url,
                data: {
                    'day': day,
                    'from_hour': from_hour,
                    'to_hour': to_hour,
                    'is_closed': is_closed,
                    'csrfmiddlewaretoken': csrf_token,
                },
                success: function(response){
                    if(response.status == 'success'){
                        if(response.is_closed){
                            html = '<tr id="hour-'+response.id+'"><td><b>'+ response.day +'</b></td><td>Closed</td><td><a href="#" class="remove_hour" data-url="/vendor/opening-hours/remove/'+response.id+'">Remove</a></td></tr>';    
                        }else{
                            html = '<tr id="hour-'+response.id+'"><td><b>'+ response.day +'</b></td><td>'+ response.from_hour +' - '+ response.to_hour +'</td><td><a href="#"class="remove_hour" data-url="/vendor/opening-hours/remove/'+response.id+'>Remove</a></td></tr>';
                        }
                        $(".opening_hours").append(html);
                        document.getElementById("opening_hours").reset();       // opening_hours is a form id
                    }else{
                        swal(response.message, '', 'error');
                    }
                }
            })
        }
        else{
            swal('Please fill the details', '', 'info');
        }

    });

    // Remove opening hour

    $(document).on('click', '.remove_hour', function(e){
        e.preventDefault();
        var url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            
            success: function(response){
                console.log(response.status)
                if (response.status == 'success'){
                    // var row_id = response['id']
                    // console.log(row_id)
                    document.getElementById('hour-'+response.id).remove()
                }
                
            }
        });
    });

    // document ready close
});

