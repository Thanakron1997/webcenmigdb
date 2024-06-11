window.addEventListener('beforeunload',function(){
    document.getElementById('loading-icon').style.display = 'flex';
  });



  $('#world-map').vectorMap({map: 'world_mill_en',
series: {
  regions: [{
    values: gdpData,
    scale: ['#C8EEFF', '#0071A4'],
    normalizeFunction: 'polynomial'
  }]
},
onRegionTipShow: function(e, el, code){
  el.html(el.html()+' (Record - '+gdpData[code]+')');
}
});

var barColors = "#619CE8";
new Chart("myChart_his_date", {
  type: "bar",
  data: {
        labels: data.map(row => row.year),
        datasets: [{
            label: 'Record in year',
            backgroundColor: barColors,
            data: data.map(row => row.count)
          }]
      },
  options: {
    legend: {display: false},
    title: {
      display: true,
      text: "Collection Date Record (Years)",
      fontSize: 25,
      fontColor: "black",
    },
    scales: {
          xAxes: [{
                   ticks: {
                    fontSize: 9
                   }
                  }],
          yAxes: [{ticks: {
                    fontSize: 9
                   }}]
            },
    plugins: {
     datalabels: {
        display: false
     }}             
    }
});




var barColors_bar_region = "#619CE8";
new Chart("myChart_bar_region", {
  type: "horizontalBar",
  data: {
    labels: xValues_bar_region,
    datasets: [{
      backgroundColor: barColors_bar_region,
      data: yValues_bar_region,
      label: 'Record',
    }]
  },
  options: {
    legend: {display: false},
    title: {
      display: true,
      text: "Sub Region Record",
      fontSize: 25,
      fontColor: "black",
    },
    scales: {
          xAxes: [{
                   ticks: {
                    fontSize: 9
                   }
                  }],
          yAxes: [{ticks: {
                    fontSize: 9
                   }}]
            },
    plugins: {
     datalabels: {
        display: false
     }}
  }
});


var barColors_pie = [
  "#005A9C",
  "#0082F0",
  "#199EF3",
  "#6FB6F6",
  "#88C6FC",
  "#B9DEFE",
  "#f0f8ff"];

new Chart("myChart_pie_organ", {
  type: "pie",
  data: {
    labels: data_organ.map(row => row.Organism),
    datasets: [{
            label: 'Record',
            backgroundColor: barColors_pie,
            data: data_organ.map(row => row.count)
          }]
  },
  options: {
    title: {
      display: true,
      text: "Organism Record",
      fontSize: 25,
      fontColor: "black",
    },
    legend: {
    display: true,
    position: 'bottom'
    },
     plugins: {
     datalabels: {
       formatter: (value, ctx) => {
         let datasets = ctx.chart.data.datasets;
         if (datasets.indexOf(ctx.dataset) === datasets.length - 1) {
           let sum = datasets[0].data.reduce((a, b) => a + b, 0);
           let percentage = Math.round((value / sum) * 100) + '%';
           return percentage;
         } else {
           return percentage;
         }
       },
       color: '#fff',
     }
   }
  }
});


var barColors_bar_st = "#619CE8";
new Chart("myChart_bar_st", {
  type: "bar",
  data: {
    labels: xValues_bar_st,
    datasets: [{
      backgroundColor: barColors_bar_st,
      data: yValues_bar_st,
      label: 'Record',
    }]
  },
  options: {
    legend: {display: false},
    title: {
      display: true,
      text: "ST Record",
      fontSize: 25,
      fontColor: "black",
    },
    scales: {
          xAxes: [{
                   ticks: {
                    fontSize: 9
                   }
                  }],
          yAxes: [{ticks: {
                    fontSize: 9
                   }}]
            },
    plugins: {
     datalabels: {
        display: false
     }}
  }
});



var barColors_pie_host = [
  "#005A9C",
  "#0082F0",
  "#199EF3",
  "#6FB6F6",
  "#88C6FC",
  "#B9DEFE",
  "#f0f8ff"];

new Chart("myChart_pie_host", {
  type: "pie",
  data: {
    labels: xValues_pie_host,
    datasets: [{
      backgroundColor: barColors_pie_host,
      data: yValues_pie_host
    }]
  },
  options: {
    title: {
      display: true,
      text: "Host Type Record",
      fontSize: 25,
      fontColor: "black",
    },
    legend: {
    display: true,
    position: 'bottom'
    },
    plugins: {
     datalabels: {
       formatter: (value, ctx) => {
         let datasets = ctx.chart.data.datasets;
         if (datasets.indexOf(ctx.dataset) === datasets.length - 1) {
           let sum = datasets[0].data.reduce((a, b) => a + b, 0);
           let percentage = Math.round((value / sum) * 100) + '%';
           return percentage;
         } else {
           return percentage;
         }
       },
       color: '#fff',
     }
   }
  }
});
