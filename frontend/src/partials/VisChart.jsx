// import plotData from "./data.json"
import React, { useEffect, useState } from "react";
import {
  VictoryBar,
  VictoryChart,
  VictoryLabel,
  VictoryGroup,
  VictoryAxis,
  VictoryContainer,
  VictoryLegend,
  VictoryTheme,
  VictoryTooltip,
  VictoryZoomContainer,
} from "victory";

import axios from "axios";

import { getOfacByPeriod } from "./DataAccessLayer";

function VisChart() {
  const [appState, setAppState] = useState();
  const [periodState, setPeriodState] = useState(false);
  const [buttonLidoState, setButtonLidoState] = useState(
    "Switch to last month"
  );
  const [buttonTitleLidoState, setButtonTitleLidoState] =
    useState("last 7 days");

  useEffect(() => {
    getData("last_week");
    console.log(appState);
  }, []);

  const getData = async (period) => {
    const data = await getOfacByPeriod(period);
    setAppState(data.data);
  };

  const handleClick = () => {
    setPeriodState((periodState) => !periodState);
    if (periodState == false) {
      getData("last_month");
      setButtonLidoState("Switch to last week");
      setButtonTitleLidoState("last 30 days");
    } else {
      getData("last_week");
      setButtonLidoState("Switch to last month");
      setButtonTitleLidoState("last 7 days");
    }
  };

  return (
    <div>
      <div class="h3 text-center">
        <h3>
          Non-OFAC and OFAC Compliance Ratio Metrics ({buttonTitleLidoState})
        </h3>
      </div>
      <br></br>
      <div class="flex flex-wrap space-x-0 space-y-16 justify-center">
        <div class="desktop:w-[1200px] desktop:h-[700px] uwdesktop:w-[1600px] uwdesktop:h-[900px] laptop:w-[900px] laptop:h-[700px]">
          <VictoryChart
            height={800}
            width={600}
            padding={{left: 150, bottom: 50, top: 50, right: 10}}
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
                barWidth={6}
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
                    dy={0}
                    style={{ fill: "black" }}
                    flyoutWidth={200}
                  />
                }
              />

              <VictoryBar
                horizontal
                barWidth={6}
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
                    dy={0}
                    style={{ fill: "black" }}
                    flyoutWidth={200}
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
              style={{ tickLabels: { fontSize: 10, fill: "#FFFFFF" } }}
              label="Lido Validator"
              axisLabelComponent={
                <VictoryLabel
                  dy={-100}
                  style={[{ fill: "#FFFFFF", fontSize: 20 }]}
                  padding={200}
                />
              }
            />
          </VictoryChart>

          <div class="h5 mb-4  px-6 py-3 text-white text-center bg-center font-extrabold rounded-full">
            <button
              type="button"
              onClick={handleClick}
              class="bg-sky-500 hover:bg-cyan-600 bg-center font-extrabold rounded-full px-6 py-3"
            >
              {buttonLidoState}
            </button>
          </div>
        </div>
        <div class=" desktop:w-[600px] tablet:w-[400px] tablet:h-[300px] laptop:w-[300px]  mr-48">
          <p class="desktop:text-xl uwdesktop:text-2xl">
            <b>For each validator we calculate:</b>
          </p>
          <br></br>
          <ol class="list-disc list-inside">
            <li class="desktop:text-xg uwdesktop:text-xl">
            The Non-OFAC Compliance Ratio is the percentage of transactions that are not compliant with OFAC regulations and are included in blocks proposed by a validator.

            </li>
            <li class="desktop:text-xg uwdesktop:text-xl">
            The OFAC Compliance Ratio is the percentage of transactions that are compliant with OFAC regulations and are included in blocks proposed by a validator.

            </li>
          </ol>
          <br></br>
          <p class="desktop:text-xg uwdesktop:text-xl">
          Example of metric calculation:
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
          Let's say that for the period, there were a total of 100,000 compliant transactions and 1,000 non-compliant transactions on the Ethereum network. Our validator included 500 compliant transactions and 2 non-compliant transactions in their blocks.
          </p>
          <br></br>
          <p>Validator’s OFAC Compliance Ratio -  500 / 100,000 = 0.5%</p>
          <p>Validator’s Non-OFAC Compliance Ratio -  2 / 1,000 = 0.2%</p>
        </div>
      </div>
    </div>
  );
}

export default VisChart;
