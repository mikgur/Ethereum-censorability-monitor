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

  useEffect(() => {
    getLatencyData()
  }, []);

  const getLatencyData = async () => {
    const data = await getLatency();
    setLatencyState(data.data);
  };

  const width = 1800;
  const height = 1800;
  return (
    <div>

      <div class="h3 text-center">
      <h3>Сensorship latency and without lido censorship</h3>
      </div>
      <br></br>
      <div class="flex space-x-0">
      <div
        class="desktop:w-[1200px] desktop:h-[700px] laptop:w-[900px] "
      >
        <VictoryChart
          height={800}
          width={1000}
          padding={{bottom:130,left:100,right:200}}
          minDomain={{ y: 0 }}
          maxDomain={{ y: 45 }}
          theme={VictoryTheme.material}
          label="Share of all transactions (OFAC - NON OFAC transactions)"
        >
        <VictoryLegend x={800} y={30}
        orientation="vertical"
        gutter={90}
        style={{labels: {fontSize: 20} }}
        data={[
          { name: "Сensorship latency", symbol: { fill: "#1e90ff" }, labels: { fill: "#FFFFFF" } },
          { name: "Lido-adjusted censorship latency", symbol: { fill: "#c43a31" }, labels: { fill: "#FFFFFF" } },
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
      <div class="desktop:w-[400px] mr-48">
      <p class="text-xl">
        <b> Censorship Latency</b>
      </p>
      <p class="text-xg indent-8">The Censorship Latency metric measures the difference in average waiting time for transactions with similar features, except for their OFAC compliance status. We use a binary classifier with high accuracy to predict the number of blocks for which non-OFAC compliant transactions were not included due to censorship. This number is then multiplied by 12 to calculate the Censorship Latency metric.</p>
        <br></br>
      <p class="text-xl">
        <b>Lido-adjusted censorship latency</b>
      </p>
        <p class="text-xg indent-8">We also compute a modified version of the Censorship Latency metric by assuming that the Lido validators do not engage in censorship. This adjusted metric helps to understand the impact of censorship by other validators on the overall network.</p>

    </div>
    </div>
    </div>
  );
}

export default LatencyChart;