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


import { getAllPool } from "./DataAccessLayer";

function PoolChart() {
  const [poolState, setPoolState] = useState();
  const [poolPeriodState, setPoolPeriodState] = useState(true);

  const [buttonPoolState, setButtonPoolState] = useState(
    "Switch to last month"
  );

  useEffect(() => {
    getPoolData("last_week")
  }, []);

  const getPoolData = async (period) => {
    const data = await getAllPool(period);
    setPoolState(data.data);
  };

  const handleClick = () => {
    setPoolPeriodState((poolPeriodState) => !poolPeriodState);
    if (poolPeriodState == false) {
      getPoolData("last_month");
      setButtonPoolState("Switch to last week");
    } else {
      getPoolData("last_week");
      setButtonPoolState("Switch to last month");
    }
  };

  const width = 1800;
  const height = 600;
  return (
    <div>
      <div class="h3 text-center">
        <h4>Lido Censorship Resistance Index and Other Validators Censorship Resistance Index(7 days/30 days)</h4>
      </div>
      <br></br>
      <div class="flex space-x-0">
      <div
        style={{
          // height: height,
          // width: width,
        }}
        class="desktop:w-[1200px] desktop:h-[200px] laptop:w-[900px]"
      >
        <VictoryChart
          height={150}
          width={700}
          padding={{bottom:50,left:100,right:100,top:50}}
          label="Lido vs rest ratio"
        >
        <VictoryBar
            horizontal
            barWidth={10}
            alignment="middle"
            style={{ data: { fill: "#1e90ff" } }}
            data={poolState}
            x="pool"
            y="ratio"
        />
          <VictoryAxis
            dependentAxis
            tickFormat={(t) => `${t}%`}
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
            axisLabelComponent={
              <VictoryLabel
                dy={-50}
                style={[{ fill: "#FFFFFF", fontSize: 17 }]}
              />
            }
          />
        </VictoryChart>
        <div class="h5 mb-4  px-6 py-3 text-white text-center bg-center font-extrabold rounded-full">
        <button type="button" onClick={handleClick} class="bg-sky-500 hover:bg-cyan-600 bg-center font-extrabold rounded-full px-6 py-3">
          {buttonPoolState}
        </button>
      </div>
      </div>
      

      <div class="desktop:w-[400px] mr-48">
      <p class="text-xl">
      We calculate Censorship Resistance Index for all the Lido validators and compare it to all the other validators in total.
      </p>
    </div>
    </div>
    </div>
  );
}

export default PoolChart;