import React, { useEffect, useState } from "react";
import {
  VictoryBar,
  VictoryChart,
  VictoryLabel,
  VictoryAxis,
  VictoryContainer,
  VictoryTooltip,
  VictoryLine
} from "victory";
import { getRatioByPeriod } from "./DataAccessLayer";

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

function RatioChart() {
  const [ratioState, setRatioState] = useState();
  const [currentPeriod, setCurrentPeriod] = useState('last_half_year');

  useEffect(() => {
    getRatioData("last_half_year");
  }, []);

  const getRatioData = async (period) => {
    const data = await getRatioByPeriod(period);

    const filteredAndSortedData = data.data
      // .filter(d => d.ratio> 0) // фильтрация
      .sort((a, b) => a.ratio - b.ratio); // сортировка

    setRatioState(filteredAndSortedData);
  };

  useEffect(() => {
    getRatioData(currentPeriod);
  }, [currentPeriod]);

  return (
    <div>
      <div class="h3 text-center">
        <h3>
          Censorship Resistance Index for Lido validators (
          {PERIODS.find((p) => p.value === currentPeriod).label})
        </h3>
      </div>
      <div class="flex flex-wrap space-x-0 justify-center mx-8 space-y-16 my-4">
        <div class="desktop:w-[1200px] desktop:h-[700px] uwdesktop:w-[1600px] uwdesktop:h-[900px] tablet:w-[400px] tablet:h-[600px] laptop:w-[900px] laptop:h-[700px]">
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
            width={600}
            padding={{ left: 150, bottom: 50, top: 50, right: 10 }}
            containerComponent={
              <VictoryContainer
                style={{
                  userSelect: "auto",
                  touchAction: "auto",
                }}
              />
            }
          >
            <VictoryBar
              horizontal
              barWidth={10}
              alignment="middle"
              data={ratioState}
              x="name"
              y="ratio"
              labels={({ datum }) => `Ratio: ${datum.ratio.toFixed(4)}`}
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
            <VictoryAxis
              dependentAxis
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
              style={{ tickLabels: { fontSize: 14, fill: "#FFFFFF" } }}
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
        <br></br>
        <br></br>
        <br></br>
        <div class="desktop:w-[300px] laptop:w-[300px] ">
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            The metric is the ratio of the share of non-OFAC compliant
            transactions included by a validator to the share of OFAC compliant
            transactions included by the same validator. This metric provides
            insight into whether a particular validator is more likely to
            include non-compliant transactions in blocks compared to compliant
            transactions.
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            The possible values of this index range from zero to infinity. An
            index of 1.0 means that the validator includes non-compliant and
            compliant transactions at the same rate. An index greater than 1.0
            means that the validator includes non-compliant transactions more
            often than compliant transactions. Conversely, an index less than
            1.0 indicates that the validator includes non-compliant transactions
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
