async function createWeatherChart(latitude, longitude) {
  try {
    // Fetch data from the API
    const response = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&hourly=temperature_2m,relative_humidity_2m&temperature_unit=fahrenheit&timezone=America%2FNew_York&forecast_days=1`);
    const data = await response.json();

    // Extract time and temperature data
    const times = data.hourly.time.map(time => new Date(time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    const temperatures = data.hourly.temperature_2m;
    const humidity = data.hourly.relative_humidity_2m;

    // Initialize UV index array with zeros
    let uvIndex = temperatures.map(() => 0);

    // Get the canvas element
    const ctx = document.getElementById('tempChart').getContext('2d');

    // Create the chart
    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: times,
        datasets: [
          {
            label: 'Temperature (°F)',
            data: temperatures,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1,
            yAxisID: 'y'
          },
          {
            label: 'UV Index',
            data: uvIndex,
            borderColor: 'rgb(255, 99, 132)',
            tension: 0.1,
            yAxisID: 'y1'
          },
          {
            label: 'Humidity (%)',
            data: humidity,
            borderColor: 'rgb(153, 102, 255)',
            tension: 0.1,
            yAxisID: 'y2'
          }
        ]
      },
      options: {
        responsive: true,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Time'
            }
          },
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: {
              display: true,
              text: 'Temperature (°F)'
            }
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            title: {
              display: true,
              text: 'UV Index'
            },
            grid: {
              drawOnChartArea: false,
            },
          },
          y2: {
            type: 'linear',
            display: true,
            position: 'right',
            title: {
              display: true,
              text: 'Humidity (%)'
            },
            grid: {
              drawOnChartArea: false,
            },
          }
        }
      }
    });

    // Array to hold UV index values
    let uvData = [];

    // Function to update UV index data
    function updateUVIndex() {
      const startHour = 9; // Start at 9am
      uvIndex = temperatures.map((_, i) => {
        const hour = new Date(data.hourly.time[i]).getHours();
        return (hour >= startHour && hour < startHour + uvData.length) ? uvData[hour - startHour] : 0;
      });
      chart.data.datasets[1].data = uvIndex;
      chart.update();
    }

    // Listen for console updates
    const originalConsoleLog = console.log;
    console.log = function (message, ...optionalParams) {
      originalConsoleLog.apply(console, [message, ...optionalParams]);
      if (typeof message === 'string' && message.startsWith('UV Index:')) {
        const uvValue = parseFloat(message.replace('UV Index:', '').trim());
        if (!isNaN(uvValue)) {
          uvData.push(uvValue);
          // Update chart when we have enough data (e.g., 9am to end of day, typically 24 values for hourly data)
          if (uvData.length >= 2) {
            updateUVIndex();
          }
        }
      }
    };

    // Function to add humidity and temperature data to div
    function updateDataDiv() {
      const dataDiv = document.getElementById('otherData');
      const startHour = 9;
      const endHour = 17;
      let content = dataDiv.innerHTML;
      let jsonData = [];

      for (let i = 0; i < times.length; i++) {
        const hour = new Date(data.hourly.time[i]).getHours();
        if (hour >= startHour && hour < endHour) {
          jsonData.push({
            "time": times[i],
            "Temperature": `${temperatures[i]}°F`,
            "Humidity": `${humidity[i]}%`
          });
        }
      }
      
      content += JSON.stringify(jsonData, null, 2);
      dataDiv.innerHTML = content;
    }

    updateDataDiv();

  } catch (error) {
    console.error('Error fetching or processing data:', error);
  }
}

// Call the function with desired latitude and longitude
createWeatherChart(40.7128, -74.0060); // Example coordinates for New York City
