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
  VictoryLine,
  VictoryScatter,
  VictoryTooltip,
} from "victory";

import { getLatency } from "./DataAccessLayer";

function LatencyChart() {
  const [latencyState, setLatencyState] = useState();

  useEffect(() => {
    getLatencyData();
  }, []);

  const getLatencyData = async () => {
    const data = await getLatency();
    setLatencyState(data.data);
  };

  return (
    <div>
      <div class="h3 text-center">
        <h3>Сensorship latency and without lido censorship</h3>
      </div>
      <br></br>
      <div class="flex flex-wrap space-x-0">
        <div class="desktop:w-[1200px] desktop:h-[700px] uwdesktop:w-[1600px] uwdesktop:h-[900px] laptop:w-[900px] ">
          <VictoryChart
            height={800}
            width={1000}
            padding={{ bottom: 130, left: 100, right: 200, top: 50 }}
            minDomain={{ y: 0 }}
            maxDomain={{ y: 25 }}
            theme={VictoryTheme.material}
            containerComponent={
              <VictoryContainer
                style={{
                  // pointerEvents: "auto",
                  userSelect: "auto",
                  touchAction: "auto",
                }}
              />
            }
          >
            <VictoryLegend
              x={800}
              y={30}
              orientation="vertical"
              gutter={90}
              style={{ labels: { fontSize: 20 } }}
              data={[
                {
                  name: "Сensorship latency",
                  symbol: { fill: "#1e90ff" },
                  labels: { fill: "#FFFFFF" },
                },
                {
                  name: "Lido-adjusted censorship latency",
                  symbol: { fill: "#c43a31" },
                  labels: { fill: "#FFFFFF" },
                },
              ]}
            />
            <VictoryLine
              alignment="middle"
              style={{ data: { stroke: "#c43a31" } }}
              data={latencyState}
              x="start_date"
              y="censorship_latency_without_lido_censorship"
            />
            <VictoryLine
              alignment="middle"
              style={{ data: { stroke: "#1e90ff" } }}
              // labels={({ datum }) => datum.y}
              data={latencyState}
              x="start_date"
              y="censorship_latency"
            />
            <VictoryScatter
              data={latencyState}
              x="start_date"
              y="censorship_latency"
              size={7}
              style={{
                data: { fill: "white" },
                labels: { fill: "white" },
              }}
              labels={({ datum }) =>
                `latency: ${datum.censorship_latency.toFixed(4)}`
              }
              labelComponent={
                <VictoryTooltip
                  dy={0}
                  style={{ fill: "black" }}
                  flyoutWidth={150}
                />
              }
            />
            <VictoryScatter
              data={latencyState}
              x="start_date"
              y="censorship_latency_without_lido_censorship"
              size={7}
              style={{
                data: { fill: "white" },
                labels: { fill: "white" },
              }}
              labels={({ datum }) =>
                `latency: ${datum.censorship_latency_without_lido_censorship.toFixed(
                  4
                )}`
              }
              labelComponent={
                <VictoryTooltip
                  dy={0}
                  style={{ fill: "black" }}
                  flyoutWidth={150}
                />
              }
            />
            <VictoryAxis
              dependentAxis
              // tickFormat={(t) => `${t}%`}
              style={{ tickLabels: { fontSize: 19, fill: "#FFFFFF" } }}
              label="LATENCY"
              tickFormat={(t) => `${t}s`}
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
          <p class="desktop:text-xl uwdesktop:text-2xl">
            <b> Censorship Latency</b>
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            The Censorship Latency metric measures the difference in average
            waiting time for transactions with similar features, except for
            their OFAC compliance status. We use a binary classifier with high
            accuracy to predict the number of blocks for which non-OFAC
            compliant transactions were not included due to censorship. This
            number is then multiplied by 12 to calculate the Censorship Latency
            metric.
          </p>
          <br></br>
          <p class="desktop:text-xl uwdesktop:text-2xl">
            <b>Lido-adjusted censorship latency</b>
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            We also compute a modified version of the Censorship Latency metric
            by assuming that the Lido validators do not engage in censorship.
            This adjusted metric helps to understand the impact of censorship by
            other validators on the overall network.
          </p>
        </div>
      </div>
    </div>
  );
}

export default LatencyChart;
