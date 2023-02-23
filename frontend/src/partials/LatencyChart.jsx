import React, { useEffect, useState } from "react";
import {
  VictoryBar,
  VictoryChart,
  VictoryLabel,
  VictoryGroup,
  VictoryAxis,
  VictoryContainer,
  VictoryLegend,
  VictoryArea,
  VictoryTheme,
  VictoryLine
} from "victory";


import { getLatency } from "./DataAccessLayer";

function LatencyChart() {
  const [latencyState, setLatencyState] = useState();
//   const [latencyPeriodState, setLatencyPeriodState] = useState(true);

//   const [buttonLatencyState, setButtonLatencyState] = useState(
//     "Switch to last month"
//   );

  useEffect(() => {
    getLatencyData()
  }, []);

  const getLatencyData = async () => {
    const data = await getLatency();
    setLatencyState(data.data);
  };

//   const handleClick = () => {
//     setLatencyPeriodState((latencyPeriodState) => !latencyPeriodState);
//     if (LatencyPeriodState == false) {
//       getLatencyData("last_month");
//       setButtonLatencyState("Switch to last week");
//     } else {
//       getLatencyData("last_week");
//       setButtonLatencyState("Switch to last month");
//     }
//   };

  const width = 1800;
  const height = 1800;
  return (
    <div>
    {/* //   <div class="h3 w-1/6 bg-indigo-500 px-8 py-6 text-white text-right bg-center font-extrabold rounded-full">
    //     <button type="button" onClick={handleClick}>
    //       {buttonLatencyState}
    //     </button>
    //   </div> */}

      <div class="h3 text-center">
      <h2>Сensorship latency and without lido censorship</h2>
      </div>

      <div
        style={{
          height: height,
          width: width,
        }}
        class=" mx-auto"
      >
        <VictoryChart
          height={1000}
          width={1100}
          padding={{bottom:130,left:100,right:200}}
          theme={VictoryTheme.material}
          label="Share of all transactions (OFAC - NON OFAC transactions)"
        >
        <VictoryLegend x={900} y={30}
        orientation="vertical"
        gutter={20}
        // style={{title: {fontSize: 5, fill: "#FFFFFF"  } }}
        height={400}
        weight={400}
        data={[
          { name: "Сensorship latency", symbol: { fill: "#1e90ff" }, labels: { fill: "#FFFFFF" } },
          { name: "Without lido censorship", symbol: { fill: "#c43a31" }, labels: { fill: "#FFFFFF" } },
        ]}
        />
        <VictoryLine
            alignment="middle"
            style={{ data: { stroke: "#1e90ff" } }}
            // labels={({ datum }) => datum.y}
            data={latencyState}
            x="start_date"
            y="censorship_latency"
        />
        <VictoryLine
            alignment="middle"
            style={{ data: { stroke: "#c43a31" } }}
            data={latencyState}
            x="start_date"
            y="censorship_latency_without_lido_censorship"
        />
          <VictoryAxis
            dependentAxis
            // tickFormat={(t) => `${t}%`}
            style={{ tickLabels: { fontSize: 19, fill: "#FFFFFF" } }}
            label="LATENCY"
            axisLabelComponent={
              <VictoryLabel
                style={[{ fill: "#FFFFFF", fontSize: 30 }]}
                dy={-60}
                padding={100}
              />
            }
          />
          <VictoryAxis
            style={{ tickLabels: { fontSize: 19, fill: "#FFFFFF" } }}
            label="DATE"
            axisLabelComponent={
              <VictoryLabel
                dy={70}
                style={[{ fill: "#FFFFFF", fontSize: 30 }]}
              />
            }
          />
        </VictoryChart>
      </div>
    </div>
  );
}

export default LatencyChart;