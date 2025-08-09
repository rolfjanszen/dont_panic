<script>
  import axios from 'axios';
  import Plotly from 'plotly.js-dist-min';

  let ticker = 'AAPL';
  let start = '2024-01-01';
  let end = new Date().toISOString().split('T')[0];
  let error = '';
  let chartEl;
  let chartCandle;

  const fetchPlot = async () => {
    error = '';
    try {
      const res_candle = await axios.post('http://localhost:8000/api/candle_stick/', {
        ticker,
        start,
        end
      });

      const res = await axios.post('http://localhost:8000/api/stock/', {
        ticker,
        start,
        end
      });

      const { dates, prices, rsi,rsi_colors, bar_start,bar_lengths,bar_colors,ticker: label } = res.data;
      const {dates_str, open_prices, close_prices, high_prices,prices_low} = res_candle.data;
      var price_plot = {
        x: dates,
        y: prices,
        type: 'scatter',
        mode: 'lines',
        name: label,
        xaxis: 'x',
        yaxis: 'y1'
      }


       const bar_chart = {
            type: 'bar',
             x: dates,        // Bar lengths
            y: bar_lengths,
           
            base: bar_start,       // Bar starting points
            marker: {
              color: bar_colors    // One color per bar
            }
          };

          
      var rsi_plot = {
        x: dates,
        y: rsi,
        type: 'scatter',
        mode: 'lines',
        name: 'rsi',
        xaxis: 'x',
        yaxis: 'y2'
        
      }

      var candlestick_plt = {
        x:dates_str,
        close: close_prices,
         decreasing: {line: {color: '#7F7F7F'}},
         high:high_prices,
           increasing: {line: {color: '#17BECF'}},
           line: {color: 'rgba(31,119,180,1)'},
           low:prices_low,
           open:open_prices,
            type: 'candlestick',
          xaxis: 'date',
            yaxis: 'val'

      }


      var candle_layout = {
        dragmode: 'zoom',
          margin: {
            r: 10,
            t: 25,
            b: 40,
            l: 60
          }};
          

      var layout = {
          grid: {rows: 2, columns: 1, pattern: 'independent'},
          barmode: 'overlay',
          dragmode: 'pan', 
          yaxis: {domain: [0.6, 1], title: 'Y Axis 1'},
          yaxis2: {domain: [0, 0.4], title: 'Y Axis 2'},

          // Shared X axis across both plots
          xaxis: {
            domain: [0, 1],
            matches: 'x2', // This links the x-axis with xaxis2
            title: 'Shared X Axis'
          },
          xaxis2: {
            domain: [0, 1],
            matches: 'x',  // Link back to xaxis
            anchor: 'y2'
          },

          height: 500,
          showlegend: true,
          title: 'Two vertically stacked plots with linked X-axis'
        };

        
      const data = [bar_chart,rsi_plot];

      // const layout = {
      //   title: `${label} Stock Price`,
      //   xaxis: { title: 'Date' },
      //   yaxis: { title: 'Price' }
      // };
      var config = {
        scrollZoom: true
        // responsive: true 
      };
      Plotly.newPlot(chartEl, data, layout, config);
      Plotly.newPlot(chartCandle, [candlestick_plt],candle_layout)
    } catch (err) {
      console.error(err);
      error = 'Could not fetch data.';
    }
  };
</script>

<main>
  <h1>📈 Stock Plot</h1>
  <div>
    <input bind:value={ticker} placeholder="Ticker (e.g. AAPL)" />
    <input type="date" bind:value={start} />
    <input type="date" bind:value={end} />
    <button on:click={fetchPlot}>Fetch Plot</button>
  </div>

  {#if error}
    <p style="color:red">{error}</p>
  {/if}

  <div bind:this={chartEl} style="width: 100%; height: 500px;"></div>
  <div bind:this={chartCandle} style="width: 100%; height: 500px;"></div>

</main>
