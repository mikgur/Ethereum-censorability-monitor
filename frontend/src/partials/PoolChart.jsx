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
  VictoryLine
} from "victory";

import { getAllPool } from "./DataAccessLayer";

const PERIODS = [
  { value: 'last_week', label: 'Last week', buttonLabel: '1w' },
  { value: 'last_month', label: 'Last month', buttonLabel: '1m' },
  { value: 'last_half_year', label: 'Last six months', buttonLabel: '6m' },
  { value: 'last_year', label: 'Last year', buttonLabel: '1y' },
]

function Button({ period, currentPeriod, setPeriod }) {
  return (
    <button
      onClick={() => setPeriod(period.value)}
      style={{
        transition: "background 0.3s ease",
        background: period.value === currentPeriod ? "#319795" : "#6b7280",
        color: period.value === currentPeriod ? "white" : "#d1d5db",
        // borderRadius: "5px",
        padding: "5px 15px",
      }}
    >
      {period.buttonLabel}
    </button>
  );
}




function PoolChart() {
  const [poolState, setPoolState] = useState();
  const [currentPeriod, setCurrentPeriod] = useState('last_half_year');


  useEffect(() => {
    getPoolData("last_half_year");
  }, []);

  useEffect(() => {
    getPoolData(currentPeriod);
  }, [currentPeriod]);

  const getPoolData = async (period) => {
    const data = await getAllPool(period);

    const filteredAndSortedData = data.data
      .filter(d => d.ratio> 0) // фильтрация
      .sort((a, b) => a.total_share - b.total_share); // сортировка

    setPoolState(filteredAndSortedData);
  };


  return (
    <div>
      <div class="h3 text-center">
        <h4>
          Lido/Non-Lido Censorship Resistance Index(
          {PERIODS.find((p) => p.value === currentPeriod).label})
        </h4>
      </div>
      <br></br>
      <div class="flex flex-wrap space-x-0 justify-center mx-8">
        <div class="desktop:w-[1200px] desktop:h-[700px] uwdesktop:w-[1600px] uwdesktop:h-[900px] tablet:w-[400px] tablet:h-[600px] laptop:w-[1000px] laptop:h-[700px]">
          <div class="flex justify-center overflow-hidden text-center mb-4">
            {PERIODS.map((period) => (
              <Button
                period={period}
                currentPeriod={currentPeriod}
                setPeriod={setCurrentPeriod}
              />
            ))}
          </div>
          <VictoryChart
            height={800}
            width={700}
            padding={{ bottom: 100, left: 100, right: 100, top: 50 }}
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
            {/* <VictoryLegend
              x={100}
              y={20}
              orientation="horizontal"
              gutter={10}
              style={{ title: { fontSize: 5, fill: "#FFFFFF" } }}
              data={[
                {
                  name: "Total share",
                  symbol: { fill: "#15bf6d" },
                  labels: { fill: "#FFFFFF" },
                },
                {
                  name: "Resistance index",
                  symbol: { fill: "#1e90ff" },
                  labels: { fill: "#FFFFFF" },
                },
              ]}
            /> */}
            {/* <VictoryGroup offset={12} colorScale={["#1e90ff", "#15bf6d"]}> */}
            <VictoryBar
              horizontal
              barWidth={10}
              alignment="middle"
              data={poolState}
              x="pool"
              y="ratio"
              labels={({ datum }) =>
                `Resistance index: ${datum.ratio.toFixed(4)}`
              }
              style={{ labels: { fill: "white" }, data: { fill: "#1e90ff" } }}
              labelComponent={
                <VictoryTooltip
                  cornerRadius={0} // Отключить закругление углов
                  style={{ fill: "white", fontSize: 17, fontFamily: "Arial" }}
                  flyoutStyle={{ fill: "#2d2d2d", stroke: "transparent" }}
                  pointerLength={0} // Отключить стрелку
                  pointerWidth={0} // Отключить стрелку
                />
              }
            />
            <VictoryLine
              style={{ data: { stroke: "red", strokeWidth: 2 } }}
              y={() => 1}
            />
            {/* <VictoryBar
                horizontal
                barWidth={10}
                alignment="middle"
                data={poolState}
                x="pool"
                y="total_share"
                labels={({ datum }) => `Total share: ${datum.total_share.toFixed(4)}`}
                style={{ labels: { fill: "white" } }}
                labelComponent={
                  <VictoryTooltip
                    cornerRadius={0} // Отключить закругление углов
                    style={{ fill: "white", fontSize: 17, fontFamily: "Arial" }}
                    flyoutStyle={{ fill: "#2d2d2d", stroke: "transparent" }}
                    pointerLength={0} // Отключить стрелку
                    pointerWidth={0} // Отключить стрелку
                  />
                }
              /> */}
            {/* </VictoryGroup> */}
            <VictoryAxis
              dependentAxis
              // tickFormat={(t) => `${t}%`}
              style={{ tickLabels: { fontSize: 11, fill: "#FFFFFF" } }}
              label="Resistance index"
              axisLabelComponent={
                <VictoryLabel
                  style={[{ fill: "#FFFFFF", fontSize: 17 }]}
                  padding={100}
                />
              }
            />
            <VictoryAxis
              style={{ tickLabels: { fontSize: 15, fill: "#FFFFFF" } }}
              label="POOL"
              // tickFormat={(t) => `${t.charAt(0).toUpperCase() + t.slice(1)}`}
              axisLabelComponent={
                <VictoryLabel
                  dy={-60}
                  style={[{ fill: "#FFFFFF", fontSize: 17 }]}
                />
              }
            />
          </VictoryChart>
        </div>

        <div class="desktop:w-[400px] mr-48">
          <p class="desktop:text-xl desktop:text-xl indent-8">
            We calculate Censorship Resistance Index for Lido at all and compare
            it to all other known pools in total.
          </p>
          <br></br>
          <p>Example of metric calculation:</p>
          <br></br>
          <p>A = OFAC Compliance Ratio calculated for pool N in total</p>
          <p>
            B = NON-OFAC Compliance Ratio calculated for the pool N in total
          </p>
          <p>Censorship Resistance Index for pool N = B / A</p>
        </div>
      </div>
    </div>
  );
}

export default PoolChart;
