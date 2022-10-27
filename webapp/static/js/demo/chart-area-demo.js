// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function number_format(number, decimals, dec_point, thousands_sep) {
  // *     example: number_format(1234.56, 2, ',', ' ');
  // *     return: '1 234,56'
  number = (number + '').replace(',', '').replace(' ', '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function(n, prec) {
      var k = Math.pow(10, prec);
      return '' + Math.round(n * k) / k;
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '').length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}

var colors = ["rgba(246, 25, 25, 0.63)", "rgba(241, 101, 21, 0.63)", "rgba(255, 186, 54, 0.63)", "rgba(131, 255, 54, 0.86)",
            "rgba(54, 255, 123, 0.78)", "rgba(65, 222, 185, 0.93)", "rgba(65, 187, 222, 0.93)", "rgba(65, 148, 222, 0.93)", 
            "rgba(65, 119, 222, 0.93)", "rgba(65, 76, 222, 0.93)", "rgba(116, 65, 222, 0.93)", "rgba(184, 65, 222, 0.93)",
            "rgba(241, 102, 236, 0.93)", "rgba(255, 135, 216, 0.93)", "rgba(165, 40, 40, 0.93)", "rgba(165, 104, 40, 0.93)", 
            "rgba(165, 133, 40, 0.93)", "rgba(161, 165, 40, 0.93)", "rgba(107, 165, 40, 0.93)", "rgba(40, 165, 101, 0.93)"]

$.ajax({
  type: 'GET',
  url: "api/data_len_by_region",
  data: {},
  dataType: 'json',
  success: function (data) {
    var regions = data['regions'];
    var x_ticks = data['x_ticks'];
    var counts = data['counts'];
    var dataset = [];

    var ctx = document.getElementById("myAreaChart");
    for(i = 0; i < regions.length; i ++){
      dataset.push({
        label: regions[i],
        lineTension: 0.3,
        backgroundColor: "#00ff0000",
        borderColor: colors[i],
        pointRadius: 3,
        pointBackgroundColor: colors[i],
        pointBorderColor: colors[i],
        pointHoverRadius: 3,
        pointHoverBackgroundColor: colors[i],
        pointHoverBorderColor: colors[i],
        pointHitRadius: 10,
        pointBorderWidth: 2,
        data: counts[i],
        });
    }
  
    var myLineChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: x_ticks,
        datasets: dataset
      },
      options: {
        maintainAspectRatio: false,
        layout: {
          padding: {
            left: 10,
            right: 25,
            top: 25,
            bottom: 0
          }
        },
        scales: {
          xAxes: [{
            time: {
              unit: 'date'
            },
            gridLines: {
              display: false,
              drawBorder: false
            },
            ticks: {
              maxTicksLimit: 7
            }
          }],
          yAxes: [{
            ticks: {
              maxTicksLimit: 5,
              padding: 10,
              // Include a dollar sign in the ticks
              callback: function(value, index, values) {
                return number_format(value);
              }
            },
            gridLines: {
              color: "rgb(234, 236, 244)",
              zeroLineColor: "rgb(234, 236, 244)",
              drawBorder: false,
              borderDash: [2],
              zeroLineBorderDash: [2]
            }
          }],
        },
        legend: {
          display: false
        },
        tooltips: {
          backgroundColor: "rgb(255,255,255)",
          bodyFontColor: "#858796",
          titleMarginBottom: 10,
          titleFontColor: '#6e707e',
          titleFontSize: 14,
          borderColor: '#dddfeb',
          borderWidth: 1,
          xPadding: 15,
          yPadding: 15,
          displayColors: false,
          intersect: false,
          mode: 'index',
          caretPadding: 10,
          callbacks: {
            label: function(tooltipItem, chart) {
              var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || ' ';
              return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
            }
          }
        }
      }
    });
    myLineChart.render(); 
  }
});

// Area Chart Example
