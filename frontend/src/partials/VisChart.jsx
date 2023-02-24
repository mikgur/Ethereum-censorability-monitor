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
} from "victory";

import axios from "axios";

import { getOfacByPeriod } from "./DataAccessLayer";

function VisChart() {
  const [appState, setAppState] = useState();
  const [periodState, setPeriodState] = useState(true);
  const [buttonLidoState, setButtonLidoState] = useState(
    "Switch to last month"
  );

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
    } else {
      getData("last_week");
      setButtonLidoState("Switch to last month");
    }

    console.log(appState);
  };

  const width = 1800;
  const height = 1800;
  return (
    <div
      style={{
        height: height,
        width: width,
      }}
      class=" mx-auto desktop:grid-cols-4"
    >
      
      <div class="h2 text-center">
        <h3>Validator’s OFAC\Non OFAC compliant share</h3>
      </div>
      <VictoryChart
        height={900}
        width={700}
        label="Share of Lido transactions (OFAC - NON OFAC compliant transactions)"
      >
        <VictoryLegend
          x={640}
          y={30}
          orientation="vertical"
          gutter={10}
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
        <VictoryGroup offset={10} colorScale={["#1e90ff", "#15bf6d"]}>
          <VictoryBar
            horizontal
            barWidth={8}
            alignment="middle"
            data={appState}
            x="name"
            y="ofac_compliant_share"
          />

          <VictoryBar
            horizontal
            barWidth={8}
            alignment="middle"
            data={appState}
            x="name"
            y="ofac_non_compliant_share"
          />
        </VictoryGroup>
        <VictoryAxis
          dependentAxis
          tickFormat={(t) => `${t}%`}
          style={{ tickLabels: { fontSize: 12, fill: "#FFFFFF" } }}
          label="Share of Lido transactions"
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
            />
          }
        />
      </VictoryChart>

      <div class="h3 mb-4  px-6 py-3 text-white text-center bg-center font-extrabold rounded-full">
        <button type="button" onClick={handleClick} class="bg-sky-500 hover:bg-cyan-600 bg-center font-extrabold rounded-full px-6 py-3">
          {buttonLidoState}
        </button>
      </div>

    </div>
  );
}

export default VisChart;
