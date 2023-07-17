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

import { getOfacByPeriod } from "./DataAccessLayer";

const PERIODS = [
  { value: 'last_week', label: 'Last week', buttonLabel: '1w' },
  { value: 'last_month', label: 'Last month', buttonLabel: '1m' },
  { value: 'last_half_year', label: 'Last six months', buttonLabel: '6m' },
  { value: 'last_year', label: 'Last year', buttonLabel: '1y' },
];

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

function VisChart() {
  const [appState, setAppState] = useState();
  const [currentPeriod, setCurrentPeriod] = useState('last_half_year');

  const getData = async (period) => {
    const data = await getOfacByPeriod(period);
    const filteredAndSortedData = data.data
      // .filter(d => d.ofac_compliant_share > 0) // фильтрация
      .sort((a, b) => a.ofac_compliant_share - b.ofac_compliant_share);
    setAppState(filteredAndSortedData);
  };

  useEffect(() => {
    getData(currentPeriod);
  }, [currentPeriod]);

  return (
    <div>
      <div class="h3 text-center">
        <h3>
          Non-OFAC and OFAC Compliance Ratio Metrics <br></br> for Lido validators ({PERIODS.find(p => p.value === currentPeriod).label})
        </h3>
      </div>
      <br/>
      <div class="flex flex-wrap space-x-0 space-y-16 justify-center">
        <div class="desktop:w-[1200px] desktop:h-[700px] uwdesktop:w-[1600px] uwdesktop:h-[900px] laptop:w-[600px] laptop:h-[700px]">
        <div class="flex justify-center overflow-hidden text-center mb-4">
            {PERIODS.map(period => (
              <Button
                period={period}
                currentPeriod={currentPeriod}
                setPeriod={setCurrentPeriod}
              />
            ))}
          </div>
          <VictoryChart
            height={900}
            width={600}
            padding={{ left: 150, bottom: 50, top: 50, right: 10 }}
            label="Share of Lido transactions (OFAC - NON OFAC compliant transactions)"
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
              x={150}
              y={0}
              orientation="horizontal"
              gutter={20}
              style={{ title: { fontSize: 5, fill: "#FFFFFF" } }}
              data={[
                {
                  name: "OFAC compliant",
                  symbol: { fill: "#1e90ff" },
                  labels: { fill: "#FFFFFF" },
                },
                {
                  name: "NON OFAC compliant",
                  symbol: { fill: "#15bf6d" },
                  labels: { fill: "#FFFFFF" },
                },
              ]}
            />
            <VictoryGroup offset={8} colorScale={["#1e90ff", "#15bf6d"]}>
              <VictoryBar
                horizontal
                barWidth={10}
                alignment="middle"
                data={appState}
                x="name"
                y="ofac_compliant_share"
                labels={({ datum }) =>
                  `Share of eth transactions:\n ${datum.ofac_compliant_share.toFixed(
                    4
                  )}`
                }
                style={{ labels: { fill: "white" } }}
                labelComponent={
                  <VictoryTooltip
                  cornerRadius={0}
                  style={{ fill: "white", fontSize: 15, fontFamily: "Arial" }}
                  flyoutStyle={{ fill: "#2d2d2d", stroke: "transparent" }}
                  pointerLength={0}
                  pointerWidth={0}
                  />
                }
              />

              <VictoryBar
                horizontal
                barWidth={10}
                alignment="middle"
                data={appState}
                x="name"
                y="ofac_non_compliant_share"
                labels={({ datum }) =>
                  `Share of eth transactions:\n ${datum.ofac_non_compliant_share.toFixed(
                    4
                  )}`
                }
                style={{ labels: { fill: "white" } }}
                labelComponent={
                  <VictoryTooltip
                  cornerRadius={0} // Отключить закругление углов
                  style={{ fill: "white", fontSize: 15, fontFamily: "Arial" }}
                  flyoutStyle={{ fill: "#2d2d2d", stroke: "transparent" }}
                  pointerLength={0} // Отключить стрелку
                  pointerWidth={0} // Отключить стрелку
                  />
                }
              />
            </VictoryGroup>
            <VictoryAxis
              dependentAxis
              tickFormat={(t) => `${t}%`}
              style={{ tickLabels: { fontSize: 12, fill: "#FFFFFF" } }}
              label="Share of eth transactions"
              axisLabelComponent={
                <VictoryLabel
                  style={[{ fill: "#FFFFFF", fontSize: 20 }]}
                  padding={100}
                />
              }
            />
            <VictoryAxis
              style={{ tickLabels: { fontSize: 15, fill: "#FFFFFF" } }}
              label="Lido Validator"
              axisLabelComponent={
                <VictoryLabel
                  dy={-140}
                  style={[{ fill: "#FFFFFF", fontSize: 20 }]}
                  padding={200}
                />
              }
            />
          </VictoryChart>
        </div>
        <div class=" desktop:w-[600px] tablet:w-[400px] tablet:h-[300px] laptop:w-[300px]  mr-48">
          <p class="desktop:text-xl uwdesktop:text-2xl">
            <b>For each validator we calculate:</b>
          </p>
          <br/>
          <ol class="list-disc list-inside">
            <li class="desktop:text-xg uwdesktop:text-xl">
            The Non-OFAC Compliance Ratio is the percentage of transactions that are not compliant with OFAC regulations and are included in blocks proposed by a validator.
            </li>
            <li class="desktop:text-xg uwdesktop:text-xl">
            The OFAC Compliance Ratio is the percentage of transactions that are compliant with OFAC regulations and are included in blocks proposed by a validator.
            </li>
          </ol>
          <br/>
          <p class="desktop:text-xg uwdesktop:text-xl">
          Example of metric calculation:
          </p>
          
          <ul class="list-disc list-inside">
            <li class="desktop:text-xg uwdesktop:text-xl">
              The validator proposed 100 blocks.
            </li>
            <li class="desktop:text-xg uwdesktop:text-xl">
              There are 1000 transactions included in these blocks.
            </li>
            <li class="desktop:text-xg uwdesktop:text-xl">
              800 transactions are OFAC compliant.
            </li>
            <li class="desktop:text-xg uwdesktop:text-xl">
              200 transactions are not OFAC compliant.
            </li>
          </ul>
          <br/>
          <p class="desktop:text-xg uwdesktop:text-xl">
            Therefore, the OFAC Compliance Ratio for this validator is 80%, and the Non-OFAC Compliance Ratio is 20%.
          </p>
        </div>
      </div>
    </div>
  );
}

export default VisChart;
