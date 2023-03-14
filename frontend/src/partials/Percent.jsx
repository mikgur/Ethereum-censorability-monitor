import React, { useEffect, useState } from "react";

import { getPercent } from "./DataAccessLayer";

function Percent() {
  const [percentState, setPercentState] = useState();

  useEffect(() => {
    getPercentData();
  }, []);

  const getPercentData = () => {
    const data = getPercent();
    
    setPercentState(data.data);
  };
  console.log(percentState);
  return (
    <div>
      <div class="h3 mx-auto w-3/4">
        <h3>
          <b>
            Of all Non-OFAC compliant transactions,{" "}
            {46}% were censored at 
            least once. Lido validators were involved in censoring of{" "}
            {23}% of Non-OFAC
            compliant transactions during last 30 days.
          </b>
        </h3>
      </div>


    </div>
  );
}

export default Percent;
