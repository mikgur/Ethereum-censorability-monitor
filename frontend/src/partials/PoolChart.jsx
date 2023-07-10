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

import { Transition } from "react-transition-group";

import { getAllPool } from "./DataAccessLayer";

const PERIODS = [
  { value: 'last_week', label: 'Last week', buttonLabel: '1w' },
  { value: 'last_month', label: 'Last month', buttonLabel: '1m' },
  { value: 'last_half_year', label: 'Last six months', buttonLabel: '6m' },
  { value: 'last_year', label: 'Last year', buttonLabel: '1y' },
]

function Button({ period, currentPeriod, setPeriod }) {
  return (
    <Transition 
      in={period.value === currentPeriod}
      timeout={200}
      unmountOnExit
    >
      {state => (
        <button
          onClick={() => setPeriod(period.value)}
          className={`
            px-4 py-2 font-extrabold rounded-none 
            transition-all ease-in-out duration-200 transform
            ${period.value === currentPeriod ? 'bg-cyan-600' : 'bg-sky-500 hover:bg-cyan-600'}
            ${state === 'entering' ? 'animate-pulse' : ''}
          `}
        >
          {period.buttonLabel}
        </button>
      )}
    </Transition>
  );
}

function PoolChart() {
  const [poolState, setPoolState] = useState();
  const [currentPeriod, setCurrentPeriod] = useState('last_week');


  useEffect(() => {
    getPoolData("last_week");
  }, []);

  useEffect(() => {
    getPoolData(currentPeriod);
  }, [currentPeriod]);

  const getPoolData = async (period) => {
    const data = await getAllPool(period);

    const filteredAndSortedData = data.data
      .filter(d => d.ratio> 0) // фильтрация
      .sort((a, b) => a.ratio - b.ratio); // сортировка

    setPoolState(filteredAndSortedData);
  };


  return (
    <div>
      <div class="h3 text-center">
        <h4>
        Lido/Non-Lido Censorship Resistance Index({PERIODS.find(p => p.value === currentPeriod).label})
        </h4>
      </div>
      <br></br>
      <div class="flex flex-wrap space-x-0 justify-center mx-8">
        <div class="desktop:w-[1200px] desktop:h-[700px] uwdesktop:w-[1600px] uwdesktop:h-[900px] tablet:w-[400px] tablet:h-[600px] laptop:w-[900px] laptop:h-[700px]">
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
            height={600}
            width={700}
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
              <VictoryBar
                horizontal
                barWidth={8}
                alignment="middle"
                data={poolState}
                x="pool"
                y="ratio"
                labels={({ datum }) => `ratio: ${datum.ratio.toFixed(4)}`}
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
