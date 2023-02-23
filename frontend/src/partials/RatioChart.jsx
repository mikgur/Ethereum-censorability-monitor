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


import {getRatioByPeriod } from "./DataAccessLayer";

function RatioChart() {
  const [ratioState, setRatioState] = useState();
  const [ratioPeriodState, setRatioPeriodState] = useState(true);

  const [buttonRatioState, setButtonRatioState] = useState(
    "Switch to last month"
  );

  useEffect(() => {
    getRatioData("last_week")
  }, []);

  const getRatioData = async (period) => {
    const data = await getRatioByPeriod(period);
    setRatioState(data.data);
  };

  const handleClick = () => {
    setRatioPeriodState((ratioPeriodState) => !ratioPeriodState);
    if (ratioPeriodState == false) {
      getRatioData("last_month");
      setButtonRatioState("Switch to last week");
    } else {
      getRatioData("last_week");
      setButtonRatioState("Switch to last month");
    }
  };

  const width = 1800;
  const height = 1800;
  return (
    <div>
      <div class="h3 w-1/6 bg-indigo-500 px-8 py-6 text-white text-right bg-center font-extrabold rounded-full">
        <button type="button" onClick={handleClick}>
          {buttonRatioState}
        </button>
      </div>

      <div class="h3 text-center">
      <h3>Share of all transactions (OFAC - NON OFAC transactions)</h3>
      </div>

      <div
        style={{
          height: height,
          width: width,
        }}
        class=" mx-auto"
      >
        <VictoryChart
          height={900}
          width={700}
          label="Share of all transactions (OFAC - NON OFAC transactions)"
        >
        <VictoryBar
            horizontal
            barWidth={8}
            alignment="middle"
            style={{ data: { fill: "#1e90ff" } }}
            data={ratioState}
            x="name"
            y="ratio"
        />
          <VictoryAxis
            dependentAxis
            tickFormat={(t) => `${t}%`}
            style={{ tickLabels: { fontSize: 12, fill: "#FFFFFF" } }}
            label="RATIO"
            axisLabelComponent={
              <VictoryLabel
                style={[{ fill: "#FFFFFF", fontSize: 20 }]}
                padding={100}
              />
            }
          />
          <VictoryAxis
            style={{ tickLabels: { fontSize: 10, fill: "#FFFFFF" } }}
            label="LIDO VALIDATOR"
            axisLabelComponent={
              <VictoryLabel
                dy={-100}
                style={[{ fill: "#FFFFFF", fontSize: 20 }]}
              />
            }
          />
        </VictoryChart>
      </div>
    </div>
  );
}

export default RatioChart;