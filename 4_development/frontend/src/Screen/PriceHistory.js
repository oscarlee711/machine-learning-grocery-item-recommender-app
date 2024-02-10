import { useRoute } from '@react-navigation/native';
import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { View, StyleSheet, Dimensions } from 'react-native';
import Svg, { Circle, G, Line, Path, Text as SvgText } from 'react-native-svg';
import api from '../core/Service';
import axios from "axios";

const xPadding = 50;
const yPadding = 20;
const screenWidth = Dimensions.get('window').width;
const chartWidth = screenWidth - xPadding * 2;

const chartHeight = 180 - yPadding * 2;
let minValue = 0;
let maxValue = 100;

const PriceHistory = () => {
    const route = useRoute();
    const token = useSelector(state => state.app.token);
    const { id } = route.params;
    const [itemListHist, setItemListHist] = useState();

    useEffect(() => { getItemHist() }, []);

    const getItemHist = async () => {
        const postobj = { id: id }
        const headers = { 'Authorization': 'Bearer ' + token }
        await axios.post(`${api}/item/searchHistory`, postobj, { headers: headers })
            .then(function (response) {
                if (response) {
                    setItemListHist(response?.data); 
                }
            })
            .catch(function (error) {
                console.warn("ERROR: " + error);
            })
        // Trim date string
        /*await itemListHist.forEach(object => {
            let day_month = object.IPH_DATE.substr(8, 2) + "/" + object.IPH_DATE.substr(5, 2);
            object.IPH_DATE = day_month;
        });*/
    }
    const [xScale, setXScale] = useState(() => (date) => 0);

    useEffect(() => {
        // Initialize xScale function here
        if (itemListHist && itemListHist.length > 0) {
            setXScale(() => (date) => ((new Date(date) - new Date(itemListHist[0].IPH_DATE.substr(0, 10))) / (280 * 60 * 60 * 24 * 30)) * (chartWidth / (itemListHist.length - 1)));
            minValue = (Math.min(...itemListHist.map((d) => d.IPH_ITEM_BASE_PRICE)));
            maxValue = (Math.max(...itemListHist.map((d) => d.IPH_ITEM_BASE_PRICE)));
            if (maxValue === 0) {
                maxValue = 100; // Set maxValue to 100
            }
        }
    }, [itemListHist]);


    const yScale = (price) => (chartHeight - (price / maxValue) * chartHeight);


    return (
        <View style={styles.container}>
            <Svg width={screenWidth} height={250}>
                <G x={xPadding} y={yPadding}>
                    {/* X-axis */}
                    <Line x1="0" y1={chartHeight} x2={chartWidth} y2={chartHeight} stroke="#ccc" strokeWidth="1" />
                    {itemListHist && itemListHist.map((d) => (
                        <React.Fragment key={d.IPH_DATE.substr(0, 10)}>
                            <Line x1={xScale(d.IPH_DATE.substr(0, 10)) + 10} y1={chartHeight} x2={xScale(d.IPH_DATE.substr(0, 10)) + 10} y2={chartHeight + 5} stroke="#ccc" strokeWidth="1" />
                            <SvgText x={xScale(d.IPH_DATE.substr(0, 10)) - 6} y={chartHeight + 18} fill="#333" fontSize="12" textAnchor="start">
                            {/* Date label */}
                                {d.IPH_DATE.substr(8, 2) + "/" + d.IPH_DATE.substr(5, 2)}
                            </SvgText>
                        </React.Fragment>
                    ))}
                    {/* Y-axis */}
                    <Line x1="0" y1="0" x2="0" y2={chartHeight} stroke="#ccc" strokeWidth="1" />
                    <SvgText x="-5" y="-10" fill="#333" fontSize="12" textAnchor="end">
                    {/* Max value label */}
                        {`$${maxValue}`}
                    </SvgText>
                    <SvgText x="-5" y={chartHeight} fill="#333" fontSize="12" textAnchor="end">
                    {/* Min value label */}
                        {`$${minValue}`}
                    </SvgText>
                    {/* First label */}
                    <SvgText x={-40} y={chartHeight + 50} fill="red" fontSize="14" fontWeight="bold" textAnchor="start">
                        Woolworths: Red
                    </SvgText>
                    {/* Second label */}
                    <SvgText x={-40} y={chartHeight + 70} fill="blue" fontSize="14" fontWeight="bold" textAnchor="start">
                        Coles: Blue
                    </SvgText>
                    {/* Data points */}
                    {itemListHist && itemListHist.map((d) => (
                        <Circle key={d.IPH_DATE.substr(0, 10)} cx={xScale(d.IPH_DATE.substr(0, 10))} cy={yScale(d.IPH_ITEM_BASE_PRICE)} r="3" fill={d.COM_ID === 2 ? "blue" : d.COM_ID === 1 ? "red" : "#007bff"} />
                    ))}
                    {/* Line connecting data points */}
                    {itemListHist && itemListHist.map((d) => (
                        <Path d={`M ${xScale(itemListHist[0].IPH_DATE.substr(0, 10))}, ${yScale(itemListHist[0].IPH_ITEM_BASE_PRICE)} ${itemListHist
                            .map((d) => `L ${xScale(d.IPH_DATE.substr(0, 10))}, ${yScale(d.IPH_ITEM_BASE_PRICE)}`)
                            .join(' ')}`} fill="none" stroke={itemListHist[0].COM_ID === 2 ? "blue" : itemListHist[0].COM_ID === 1 ? "red" : "#007bff"} strokeWidth="2" />
                    ))}
                </G>
            </Svg>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        backgroundColor: '#fff',
        paddingHorizontal: 10,
        paddingVertical: 20
    },
    date: {
        fontSize: 16
    },
    price: {
        fontSize: 16,
        fontWeight: "bold"
    }
});

export default PriceHistory;