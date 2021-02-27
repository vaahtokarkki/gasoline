import axios from 'axios'

const geocode = async (lat, lon) => {
    if (!lat || !lon) return
    try {
        const { data } = await axios.get(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`)
        if (!data.address) return ''
        return `${data.address.road} ${data.address.city}`
    } catch(e) {

    }

}

export default geocode
