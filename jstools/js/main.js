

// using jQuery
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

//btnReset
$("#btnReset").click(function (e) {
e.preventDefault();
console.log("Clear Reset");
location.reload();
});

$("#btnRUN").click(function (e) {
  // preventing from page reload and default actions
  e.preventDefault();
  openModal();
  setTimeout(() => {
    document.querySelector('.main-modal').style.display = 'none';
  }, 1000);
  // serialize the data for sending the form data.
  //var serializedData = $(this).serialize();
  //data: JSON.stringify(somedata), 
  // make POST ajax call

  var csrftoken = getCookie('csrftoken');
  console.log("click");
  console.log("csrftoken : "+csrftoken);
  //console.log("click"+$("#txtVpu").val());

  var formData = {
    //csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
    csrfmiddlewaretoken:csrftoken,
    vpu: $("#txtVpu").val(),
    fixmvasc: $("#txtMVAsc").val(),
    tab: $("#txtTap").val(),
    percenz: $("#txtPercenZ").val(),
    type: $('input[name="rdoType"]:checked').val(),
    length: $("#txtLenght").val(),

    h01_kw: $("#txtH1_pKw").val(),
    h01_pf: $("#txtH1_Pf").val(),
    sg01pf: $('input[name="rdoH1_signPF"]:checked').val(),

    h02_kw: $("#txtH2_pKw").val(),
    h02_pf: $("#txtH2_Pf").val(),
    sg02pf: $('input[name="rdoH2_signPF"]:checked').val(),

    h03_kw: $("#txtH3_pKw").val(),
    h03_pf: $("#txtH3_Pf").val(),
    sg03pf: $('input[name="rdoH3_signPF"]:checked').val(),

    batt_kw: $("#txtBatt_pKw").val(),
    batt_pf: $("#txtBatt_Pf").val(),
    sgBattPkw: $('input[name="rdoBatt_signPkw"]:checked').val(),
    sgBattPF: $('input[name="rdoBatt_signPF"]:checked').val(),


    evBattKw: $("#txtEVBatt_pKw").val(),
    evBattPf: $("#txtEVBatt_Pf").val(),
    sgEVBattPkw: $('input[name="rdoEV_signPkw"]:checked').val(),
    sgEVBattPF: $('input[name="rdoEV_signPF"]:checked').val(),

  };

   /*$.post("{% url 'process_backend' %}", { 
      headers:{
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
      },
       item_text: data,
       csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
   });*/

   console.log(formData);
  
  $.ajax({
      type: 'POST',
      url: "{% url 'calldss' %}", //process_backend
      data: formData,
      success: function (response) {
          // on successfull 
          //alert(response["responseJSON"]["success"])
          console.log('result return');
          console.log(response.raw);
          console.log(response);
          //$("#chart_img").show();
          
          //var ctx = document.getElementById('canvas-chart').getContext('2d');

          if (response.raw) {
            /*var img = new Image();
            img.onload = function() {
                //ctx.drawImage(img, 0, 0);
            };
            img.src = "{% static 'images/' %}"+response.fileName;*/
            //img.src = "'data:image/  png;base64," + response.raw+"'";
            //$("#canvas-chart").show();

            $("#chart_img").attr("src","{% static 'images/solve/' %}"+response.fileName);
            $("#chart_img").show();

            $("#resultLVV1").html(response.output_lv.V1);
            $("#resultLVV2").html(response.output_lv.V2);
            $("#resultLVV3").html(response.output_lv.V3);

            $("#resultP1kw").html(response.line.PV1);
            $("#resultP2kw").html(response.line.PV2);
            $("#resultP3kw").html(response.line.PV3);

            $("#resultQ1kvar").html(response.kilojoule.PV1);
            $("#resultQ2kvar").html(response.kilojoule.PV2);
            $("#resultQ3kvar").html(response.kilojoule.PV3);

            $("#resultPCCV1").html(response.output_pcc.V1);
            $("#resultPCCV2").html(response.output_pcc.V2);
            $("#resultPCCV3").html(response.output_pcc.V3);

            //resultPloss
            //resultQloss
            $("#resultPloss").html(response.losses.p_loss);
            $("#resultQloss").html(response.losses.q_loss);
    
          }

      },
      error: function (response) {
          // alert the error if any error occured
          console.log('response')
          //alert(response["responseJSON"]["error"])
      }
  })
  
});