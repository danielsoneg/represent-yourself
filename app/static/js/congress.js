article = $('article#content');

showLegislators = function(ret) {
  console.log(ret);
  legislators = ret.data
  house = Mustache.to_html(list,{'reps':legislators.house});
  senate = Mustache.to_html(list,{'reps':legislators.senate});
  body = Mustache.to_html(body,{'district':legislators.district,'house':house,'senate':senate});
  article.html(body);
};

sendLocation = function(location) {
    /* Send lat/long to server */
    $.ajax({
     type: "POST",
     url: '/loc',
     data: "lat=" + location.coords.latitude + "&lon=" + location.coords.longitude,
     dataType: 'json',
     success: showLegislators
    });
};

jQuery(document).ready(function($) {
  navigator.geolocation.getCurrentPosition(sendLocation);
});