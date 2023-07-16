import axios from "axios";

export const getOfacByPeriod = async (period) => {
    const data = await axios.get(`https://eth.neutralitywatch.com:443/metrics/lido_validators_share/${period}`)
    return data
}

export const getRatioByPeriod = async (period) => {
    const data = await axios.get(`https://eth.neutralitywatch.com:443/metrics/lido_validators_ratio/${period}`)
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