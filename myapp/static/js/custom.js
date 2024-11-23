let autocomplete;

function initAutoComplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById("id_address"),
    {
      types: ["geocode", "establishment"],
      componentRestrictions: { country: ["NP"] },
    }
  );
  autocomplete.addListener("place_changed", onPlacedChanged);
}
function onPlacedChanged() {
    // Get place details from the autocomplete object
    let place = autocomplete.getPlace();
  
    if (!place.geometry) {
      // If no geometry is returned, prompt user to type a valid address
      document.getElementById("id_address").placeholder = "Start typing...";
      return ;
    } else 
    {
    }

    var geocoder = new google.maps.Geocoder();
    var address = document.getElementById("id_address").value;
    geocoder.geocode({ address: address }, function (results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        var latitude = results[0].geometry.location.lat();
        var longitude = results[0].geometry.location.lng();
        console.log(latitude, longitude);
        if(window.location.pathname=='/')
          {
            $('#id_latitude').val(latitude)
            $('#id_longitude').val(longitude)
          }
          else{
            initAutoComplete1(latitude,longitude)
          }
        
      }
    });
  

  
}

  function initAutoComplete1(latitude, longitude) {
    let map;
    let marker;
     document.getElementById('map').style.display='block'
    // Initialize the map
    map = new google.maps.Map(document.getElementById("map"), {
      center: { lat:  latitude, lng:longitude  }, // Default location (Kathmandu, Nepal)
      zoom: 13,
      mapTypeId: google.maps.MapTypeId.HYBRID,
    });

  
    // Center the map on the given latitude and longitude
    
  
    // Add or update the marker
    if (marker) {
      marker.setMap(null); // Remove the existing marker, if any
    }
  
    marker = new google.maps.Marker({
      position: { lat: latitude, lng: longitude },
      map: map,
      draggable:true,
      title: "Selected Location", // You can replace this with `place.name` if applicable
    });
    marker.addListener('dragend',()=>{
      const position=marker.getPosition()
      const lat=position.lat()
      const lng=position.lng()
      $("#id_latitude").val(lat);
      $("#id_longitude").val(lng);
      const geocoder = new google.maps.Geocoder();
      const latlng = { lat: lat, lng: lng };
      geocoder.geocode({ location: latlng }, (results, status) => {
        if (status === "OK") {
         
         $("#id_address").val(results[0].address_components[0].short_name);
          if (results) {
            // Full formatted address
            for (var i = 0; i < results[0].address_components.length; i++) 
              {
            for (var j = 0; j < results[0].address_components[i].types.length; j++) {
              if (results[0].address_components[i].types[j] == "country") {
                $("#id_country").val(results[0].address_components[i].long_name);
              }
              if (
                results[0].address_components[i].types[j] == "administrative_area_level_1"
              ) {
                $("#id_state").val(results[0].address_components[i].long_name);
              }
              if (results[0].address_components[i].types[j] == "postal_code") {
                $("#id_pin_code").val(results[0].address_components[i].long_name);
              }
            }
          }
          }
        }
        })
      
    })
  }
  $(document).ready(function()
  {
    $(".add_to_cart").on("click",function(e){
      e.preventDefault();
      data_id=$(this).attr("data-id")
      data_url=$(this).attr("data-url")
      $.ajax({
        type:'GET',
        url:data_url,
        success:function(response)
        {
          if(response.status=='login_required')
            {
                  swal(response.message,"please login in",'info').then(
                    function(){
                      window.location="/accounts/login/"
                    }
                  )
            } 
            else if(response.status=='Failed')
            {
              swal(response.message,"","error")
            }
            else{
              $('#qty-'+data_id).html(response.quantity)
              $('#cart_counter').html(response.get_cart_count['cart_count'])

              if(window.location.pathname=='/cart/')
              {
                applyCartAmount(response.cart_amount['subtotal'],response.cart_amount['tax_dict'],response.cart_amount['grand_total'])
              }
              
            }
        }
      })

    })
    $(".decrease_cart").on("click",function(e){
      e.preventDefault()
      data_url=$(this).attr('data-url')
      data_id=$(this).attr('data-id')
      cart_id=$(this).attr('id')
      $.ajax({
        type:'GET',
        url:data_url,
        success:function(response){
          if(response.status=='login_required')
          {
            swal(response.message,"please login in",'info').then(
              function(){
                window.location="/accounts/login/"
              }
            )

          }
          else if(response.status=='Failed')
          {
            swal(response.message,"","error")
          }
          else{
             
            $('#qty-'+data_id).html(response.quantity)
             $('#cart_counter').html(response.get_cart_counter['cart_count'])
             if (window.location.pathname=='/cart/' && response.quantity==0)
             {
               removeCartItem(response.quantity ,cart_id)

             }
             if(window.location.pathname=='/cart/')
             {
              applyCartAmount(response.cart_amount['subtotal'],response.cart_amount['tax_dict'],response.cart_amount['grand_total'])
             }

          }

        }
      })
    })
    $('.delete_cart').on('click',function(e)
  {
    e.preventDefault()
    cart_id=$(this).attr('data-id')
    cart_url=$(this).attr('data-url')
    $.ajax({
      type:'GET',
      url:cart_url ,
      success:function(response){
        if(response.status=='login_required')
        {
          swal(response.message,'',"info").then(
            function(){
              window.location="/accounts/login/"
            })
        }
        else if (response.status=='Failed')
        {
          swal(response.message,"",'info')
        }
        else{
          $("#cart_counter").html(response.cart_counter['cart_count'])
          swal(response.status,response.message,'info')
          applyCartAmount(response.cart_amount['subtotal']
            ,response.cart_amount['tax_dict'],
            response.cart_amount['grand_total'])
          removeCartItem(0,cart_id)
          

        }


           
           
        

      }

    })
  })
  function removeCartItem(cartItemqty,cart_id){
    if (cartItemqty<=0)
    {
      document.getElementById('cart-item-'+cart_id).remove()
      checkEmptyCart();
    }


  }
  function checkEmptyCart()
  {
    var cart_counter=document.getElementById('cart_counter').innerHTML
    if(cart_counter==0)
    {
      document.getElementById('empty-cart').style.display="block" ;
    }
  }
  function applyCartAmount(subtotal,tax_dict,grand_total)
  {
    $('#subtotal').html(subtotal)
    
    $('#total').html(grand_total)
    

    for(key1 in tax_dict)
    {
      for (key2 in tax_dict[key1])
      {
        
        $('#tax-'+key1).html(tax_dict[key1][key2])
      }
    }

  }
   $('.add_hour').on('click',function(e){
     e.preventDefault()
     var day=document.getElementById('id_day').value
     var from_hour=document.getElementById('id_from_hour').value
     var to_hour=document.getElementById('id_to_hour').value
     var is_closed=document.getElementById('id_is_closed').Checked
     var csrf_token=$('input[name=csrfmiddlewaretoken]').val()
     var url=document.getElementById('add_hour_url').value

     if(is_closed)
     {
        is_closed='True'
        condition="day!=''"
     }
     else{
       is_closed='False'
       condition="day!='' && from_hour!='' && to_hour!=''"

     }
     if(eval(condition))
     {
      $.ajax({
        type:'POST',
        url:url,
        data:{
          'day':day,
          'from_hour':from_hour,
          'to_hour':to_hour,
          'is_closed':is_closed,
          'csrfmiddlewaretoken':csrf_token
        },
        success:function(response)
        {
          if(response.status=='success')
          {
            console.log(response)
            if(response.is_closed=='closed')
            {
              html=html='<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>closed</td><td><a href="" class="remove_hour" data-url="/vendor/opening_hours/remove/'+response.id+'/">Remove</a></td></tr>'
            }
            else{
              html='<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td><b>'+response.from_hour+'</b>-<b>'+response.to_hour+'</b></td><td><a href="" class="remove_hour" data-url="/vendor/opening_hours/remove/'+response.id+'/">Remove</a></td></tr>'
            }
            $('.opening_hours').append(html)
           document.getElementById('opening_hours').reset();
          }
          else{
            console.log(response.error)
          swal(response.message,'','info')

          }
          
        }

      })

     }
     else{
      swal('Please fill all the fields','','info')
      

     }

   })
    $('.remove_hour').on('click',function(e)
  {
    e.preventDefault()
    const scrollPosition=window.scrollY;
    url=$(this).attr('data-url')
    $.ajax({
      type:'GET',
      url:url,
      success:function(response)
      {
        if(response.status=='success')
        {
          document.getElementById('hour-'+response.id).remove()
          window.scrollTo(0,scrollPosition)
        }
      }
    })
  })
  $(document).on('click','.remove_hour',function(e){
    e.preventDefault()
    const scrollPosition=window.scrollY
    url=$(this).attr('data-url')
    $.ajax({
      type:'GET',
      url:url,
      success:function(response)
      {
        if(response.status=='success')
          {
            document.getElementById('hour-'+response.id).remove()
            window.scrollTo(0, scrollPosition);
          }
      }
    })
  })
    $(".item_qty").each(function () {
      var the_id = $(this).attr("id");
      var qty = $(this).attr("data-qty");
      $("#" + the_id).html(qty);
    });
    
  }
)
document.addEventListener('DOMContentLoaded', function () {
  const toggleButton = document.querySelector('.reviews-sortby-active');
  const dropdown = document.querySelector('.delivery-dropdown');

  toggleButton.addEventListener('click', function (event) {
      event.preventDefault(); // Prevent default link behavior
      dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
  });
});

  
     