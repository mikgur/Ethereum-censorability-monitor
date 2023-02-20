import axios from "axios";

export const getOfacByPeriod = async (period) => {
    const data = await axios.get(`http://127.0.0.1:8000/data/total_validators_share/${period}`)
    return data
}

export const getRatioByPeriod = async (period) => {
    const data = await axios.get(`http://127.0.0.1:8000/data/lido_validators_ratio/${period}`)
    return data
}