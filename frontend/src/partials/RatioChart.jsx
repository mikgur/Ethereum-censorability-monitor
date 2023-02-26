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
  VictoryZoomContainer,
} from "victory";

import { getRatioByPeriod } from "./DataAccessLayer";

function RatioChart() {
  const [ratioState, setRatioState] = useState();
  const [ratioPeriodState, setRatioPeriodState] = useState(true);

  const [buttonRatioState, setButtonRatioState] = useState(
    "Switch to last month"
  );

  const [buttonTitleRatioState, setButtonTitleRatioState] =
    useState("last 7 days");

  useEffect(() => {
    getRatioData("last_week");
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
      setButtonTitleRatioState("last 30 days");
    } else {
      getRatioData("last_week");
      setButtonRatioState("Switch to last month");
      setButtonTitleRatioState("last 7 days");
    }
  };

  return (
    <div>
      <div class="h3 text-center">
        <h3>Censorship Resistance Index({buttonTitleRatioState})</h3>
      </div>
      <div class="flex flex-wrap space-x-0">
        <div class="desktop:w-[1200px] desktop:h-[700px] uwdesktop:w-[1600px] uwdesktop:h-[900px] tablet:w-[400px] tablet:h-[300px] laptop:w-[900px] ">
          <VictoryChart
            height={700}
            width={500}
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
            <VictoryBar
              horizontal
              barWidth={8}
              alignment="middle"
              data={ratioState}
              x="name"
              y="ratio"
              labels={({ datum }) => `Ratio: ${datum.ratio.toFixed(4)}`}
              style={{ labels: { fill: "white" }, data: { fill: "#1e90ff" } }}
              labelComponent={
                <VictoryTooltip
                  dy={0}
                  style={{ fill: "black" }}
                  flyoutWidth={100}
                />
              }
            />
            <VictoryAxis
              dependentAxis
              // tickFormat={(t) => `${t}%`}
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

          <div class="h5 text-white text-center bg-center font-extrabold rounded-full">
            <button
              type="button"
              onClick={handleClick}
              class="bg-sky-500 hover:bg-cyan-600 bg-center font-extrabold rounded-full px-6 py-3"
            >
              {buttonRatioState}
            </button>
          </div>
        </div>
        <br></br>
        <br></br>
        <br></br>
        <div class="desktop:w-[400px] mr-48">
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            The metric we calculate is the ratio of the share of non-OFAC
            compliant transactions included by a validator to the share of OFAC
            compliant transactions included by the same validator. This metric
            provides insight into whether a particular validator is more likely
            to include non-compliant transactions in blocks compared to
            compliant transactions.
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            The possible values of this index range from zero to infinity. An
            index of one means that the validator includes non-compliant and
            compliant transactions at the same rate. An index greater than one
            means that the validator includes non-compliant transactions more
            often than compliant transactions. Conversely, an index less than
            one indicates that the validator includes non-compliant transactions
            less frequently than compliant transactions. Overall, a low
            Censorship Resistance Index could be an indication of potential
            censorship by a validator.
          </p>
        </div>
      </div>
    </div>
  );
}

export default RatioChart;
