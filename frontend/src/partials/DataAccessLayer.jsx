import axios from "axios";

export const getOfacByPeriod = async (period) => {
    const data = await axios.get(`http://127.0.0.1:8000/metrics/lido_validators_share/${period}`)
    return data
}

export const getRatioByPeriod = async (period) => {
    const data = await axios.get(`http://127.0.0.1:8000/metrics/lido_validators_ratio/${period}`)
    return data
}

export const getAllPool = async (period) => {
    const data = await axios.get(`http://127.0.0.1:8000/metrics/lido_vs_rest_share/${period}`)
    return data
}

export const getLatency = async () => {
    const data = await axios.get(`http://127.0.0.1:8000/metrics/latency`)
    for (let i = 0; i < data.data.length; i++) {
        data.data[i]['start_date'] = data.data[i]['start_date'] + '\n — \n' + data.data[i]['end_date']
    }
    return data
}