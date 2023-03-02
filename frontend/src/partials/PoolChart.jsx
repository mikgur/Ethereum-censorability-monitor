import React, { useEffect, useState } from "react";
import {
  VictoryBar,
  VictoryChart,
  VictoryLabel,
  VictoryGroup,
  VictoryAxis,
  VictoryContainer,
  VictoryLegend,
  VictoryTooltip,
} from "victory";

import { getAllPool } from "./DataAccessLayer";

function PoolChart() {
  const [poolStateWeek, setPoolStateWeek] = useState();
  const [poolStateMonth, setPoolStateMonth] = useState();

  useEffect(() => {
    getPoolDataWeek("last_week");
    getPoolDataMonth("last_month");
  }, []);

  const getPoolDataWeek = async (period) => {
    const data = await getAllPool(period);
    setPoolStateWeek(data.data);
  };

  const getPoolDataMonth = async (period) => {
    const data = await getAllPool(period);
    setPoolStateMonth(data.data);
  };

  return (
    <div>
      <div class="h3 text-center">
        <h4>
        Lido Censorship Resistance Index and Non-Lido validators Censorship Resistance Index
        </h4>
      </div>
      <br></br>
      <div class="flex flex-wrap space-x-0 justify-center mx-8">
        <div class="desktop:w-[1200px] desktop:h-[200px] uwdesktop:w-[1600px] uwdesktop:h-[300px] tablet:w-[400px] tablet:h-[300px] laptop:w-[900px]">
          <VictoryChart
            height={170}
            width={600}
            padding={{ bottom: 50, left: 100, right: 100, top: 50 }}
            label="Lido vs rest ratio"
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
              x={500}
              y={30}
              orientation="vertical"
              gutter={10}
              style={{ title: { fontSize: 5, fill: "#FFFFFF" } }}
              data={[
                {
                  name: "Last week",
                  symbol: { fill: "#15bf6d" },
                  labels: { fill: "#FFFFFF" },
                },
                {
                  name: "Last month",
                  symbol: { fill: "#1e90ff" },
                  labels: { fill: "#FFFFFF" },
                },
              ]}
            />
            <VictoryGroup offset={12} colorScale={["#1e90ff", "#15bf6d"]}>
              <VictoryBar
                horizontal
                barWidth={10}
                alignment="middle"
                data={poolStateWeek}
                x="pool"
                y="ratio"
                labels={({ datum }) => `ratio: ${datum.ratio.toFixed(4)}`}
                style={{ labels: { fill: "white" } }}
                labelComponent={
                  <VictoryTooltip
                    dy={0}
                    style={{ fill: "black" }}
                    flyoutWidth={100}
                  />
                }
              />
              <VictoryBar
                horizontal
                barWidth={10}
                alignment="middle"
                data={poolStateMonth}
                x="pool"
                y="ratio"
                labels={({ datum }) => `ratio: ${datum.ratio.toFixed(4)}`}
                style={{ labels: { fill: "white" } }}
                labelComponent={
                  <VictoryTooltip
                    dy={0}
                    style={{ fill: "black" }}
                    flyoutWidth={100}
                  />
                }
              />
            </VictoryGroup>
            <VictoryAxis
              dependentAxis
              // tickFormat={(t) => `${t}%`}
              style={{ tickLabels: { fontSize: 11, fill: "#FFFFFF" } }}
              label="RATIO"
              axisLabelComponent={
                <VictoryLabel
                  style={[{ fill: "#FFFFFF", fontSize: 17 }]}
                  padding={100}
                />
              }
            />
            <VictoryAxis
              style={{ tickLabels: { fontSize: 11, fill: "#FFFFFF" } }}
              label="POOL"
              // tickFormat={(t) => `${t.charAt(0).toUpperCase() + t.slice(1)}`}
              axisLabelComponent={
                <VictoryLabel
                  dy={-50}
                  style={[{ fill: "#FFFFFF", fontSize: 17 }]}
                />
              }
            />
          </VictoryChart>
        </div>

        <div class="desktop:w-[400px] mr-48">
          <p class="desktop:text-xl desktop:text-xl indent-8">
            We calculate Censorship Resistance Index for all the Lido validators
            and compare it to all the other validators in total.
          </p>
          <br></br>
          <p>Example of metric calculation:</p>
          <br></br>
          <p>A = OFAC Compliance Ratio calculated for all Lido validators in total (as if they are one big validator)</p>
          <p>B = NON-OFAC Compliance Ratio calculated for all Lido validators in total (as if they are one big validator)</p>
          <p>Lido metric = B / A</p>
          <br></br>
          <p>C = OFAC Compliance Ratio calculated for all Non-Lido validators in total (as if they are one big validator)</p>
          <p>D = NON-OFAC Compliance Ratio calculated for all Non-Lido validators in total (as if they are one big validator)</p>
          <p>Non-Lido validators metric = D / C</p>
        </div>
      </div>
    </div>
  );
}

export default PoolChart;
