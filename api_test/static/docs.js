var $doc = $(document);
$doc.ready(function () {
  $('[data-toggle=offcanvas]').click(function () {
    $('.row-offcanvas').toggleClass('active')
  });
});

// $.getJSON('xxxjavascript/api.json', function(data) {
//     var data={data:data};
//     var apiList = '{@each data as it}\
//         <a href="javascript:;" class="list-group-item apiGather" data="${it.fileName}">${it.name}</a>\
//         <ul class="nav apiList none" name="${it.name}">\
// 		    {@each it.info as list}<li><a href="#${list.apiFileName}" data="${list.apiFileName}" class="getApiInfo" name="${it.fileName}">${list.apiName}<p>${list.apiFileName}</p></a></li>{@/each}\
//         </ul>{@/each}';
//     var $apiList = $('#api_main');
//     var h = juicer(apiList,data);
//     $apiList.append(h);
// });

$doc.on('click','.apiGather',function (){
    var name = $(this).text(),$apiGather = $('.apiGather'),
        $api = $('.apiList[name="'+name+'"]');
    $(this).toggleClass('active');
    $api.slideToggle();
});

