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

var barColors_pie = [
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
      backgroundColor: barColors_pie,
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

new Chart("st1", {
  type: "pie",
  data: {
    labels: testdata["Salmonella enterica"].keys,
    datasets: [{
      backgroundColor: barColors_pie,
      data: testdata["Salmonella enterica"].values
    }]
  },
  options: {
    title: {
      display: true,
      text: "ST: Salmonella enterica",
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

new Chart("linage_mycobacterium", {
  type: "pie",
  data: {
    labels: testdata["Mycobacterium tuberculosis"].keys,
    datasets: [{
      backgroundColor: barColors_pie,
      data: testdata["Mycobacterium tuberculosis"].values
    }]
  },
  options: {
    title: {
      display: true,
      text: "Lineage: Mycobacterium tuberculosis",
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

new Chart("st_staphylococcus", {
  type: "pie",
  data: {
    labels: testdata["Staphylococcus aureus"].keys,
    datasets: [{
      backgroundColor: barColors_pie,
      data: testdata["Staphylococcus aureus"].values
    }]
  },
  options: {
    title: {
      display: true,
      text: "ST: Staphylococcus aureus",
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

new Chart("st_streptococcus", {
  type: "pie",
  data: {
    labels: testdata["Streptococcus agalactiae"].keys,
    datasets: [{
      backgroundColor: barColors_pie,
      data: testdata["Streptococcus agalactiae"].values
    }]
  },
  options: {
    title: {
      display: true,
      text: "ST: Streptococcus agalactiae",
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

new Chart("st_burkholderia", {
  type: "pie",
  data: {
    labels: testdata["Burkholderia pseudomallei"].keys,
    datasets: [{
      backgroundColor: barColors_pie,
      data: testdata["Burkholderia pseudomallei"].values
    }]
  },
  options: {
    title: {
      display: true,
      text: "ST: Burkholderia pseudomallei",
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

new Chart("st_candida", {
  type: "pie",
  data: {
    labels: testdata["Candida glabrata"].keys,
    datasets: [{
      backgroundColor: barColors_pie,
      data: testdata["Candida glabrata"].values
    }]
  },
  options: {
    title: {
      display: true,
      text: "ST: Candida glabrata",
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

let slideIndex = 1;
        showSlides(slideIndex);
        
        function plusSlides(n) {
          showSlides(slideIndex += n);
        }
        
        function currentSlide(n) {
          showSlides(slideIndex = n);
        }
        
        function showSlides(n) {
          let i;
          let slides = document.getElementsByClassName("mySlides");
          let dots = document.getElementsByClassName("dot");
          if (n > slides.length) {slideIndex = 1}    
          if (n < 1) {slideIndex = slides.length}
          for (i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";  
          }
          for (i = 0; i < dots.length; i++) {
            dots[i].className = dots[i].className.replace(" active_slide", "");
          }
          slides[slideIndex-1].style.display = "block";  
          dots[slideIndex-1].className += " active_slide";
        }

