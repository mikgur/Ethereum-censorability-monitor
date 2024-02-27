import axios from "axios";

export const getOfacByPeriod = async (period) => {
    const data = await axios.get(`https://eth.neutralitywatch.com:443/metrics/lido_validators_share/${period}`)

    let chainLayerCompliantShare = 0;
    let chainLayerNonCompliantShare = 0;

    const chainLayerIndex = data.data.findIndex(element => element.name === "SkillZ");
    if (chainLayerIndex !== -1) {
    chainLayerCompliantShare = data.data[chainLayerIndex].ofac_compliant_share;
    chainLayerNonCompliantShare = data.data[chainLayerIndex].ofac_non_compliant_share;
    data.data.splice(chainLayerIndex, 1);
    }

    const targetElementIndex = data.data.findIndex(element => element.name === "Kiln");
    if (targetElementIndex !== -1) {
        data.data[targetElementIndex].ofac_compliant_share += chainLayerCompliantShare;
        data.data[targetElementIndex].ofac_non_compliant_share += chainLayerNonCompliantShare;
    }
    return data
}

export const getRatioByPeriod = async (period) => {
    const data = await axios.get(`https://eth.neutralitywatch.com:443/metrics/lido_validators_ratio/${period}`)
    
    let skillzRatio = 0;
    const skillzIndex = data.data.findIndex(element => element.name === "SkillZ");
    if (skillzIndex !== -1) {
        skillzRatio = data.data[skillzIndex].ratio;
        data.data.splice(skillzIndex, 1);
    }

    const kilnIndex = data.data.findIndex(element => element.name === "Kiln");
    if (kilnIndex !== -1) {
        data.data[kilnIndex].ratio += skillzRatio;
    }
    return data
}

export const getAllPool = async (period) => {
    const data = await axios.get(`https://eth.neutralitywatch.com:443/metrics/lido_vs_rest_share/${period}`)
    return data
}

export const getLatency = async () => {
    const data = await axios.get(`https://eth.neutralitywatch.com:443/metrics/overall_latency`)
    for (let i = 0; i < data.data.length; i++) {
        data.data[i]['range_date'] = data.data[i]['start_date'] + '\n — \n' + data.data[i]['end_date']
    }
    return data
}

export const getCensoredLatency = async (period) => {
    const data = await axios.get(`https://eth.neutralitywatch.com/metrics/censored_latency/average`)
    for (let i = 0; i < data.data.length; i++) {
        data.data[i]['range_date'] = data.data[i]['start_date'] + '\n — \n' + data.data[i]['end_date']
    }
    return data
}

export const getPercent = () => {
    const data = axios.get(`https://eth.neutralitywatch.com/metrics/censored_percentage/last_month`)
    return data
}