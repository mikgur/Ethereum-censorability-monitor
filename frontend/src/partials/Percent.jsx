import React, { useEffect, useState } from "react";

import { getPercent } from "./DataAccessLayer";

function Percent() {
  const [percentState, setPercentState] = useState(null);

  useEffect(() => {
    getPercentData();
  }, []);

  const getPercentData = async () => {
    const data = await getPercent();
    setPercentState(data.data[0]);
  };

  return (
    <div>
      <div class="h3 mx-auto w-3/4">
        <h3>
          <b>
          {percentState ? (
            `Of all Non-OFAC compliant transactions, ${percentState.censored_percentage.toFixed(1)}% were censored at 
            least once. Lido validators were involved in censoring of ${percentState.lido_censored_percentage.toFixed(1)}% of Non-OFAC
            compliant transactions during last 30 days.`
          ) : (
            "Loading..."
          )}
          </b>
        </h3>
      </div>


    </div>
  );
}

export default Percent;
