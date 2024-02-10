import { useNavigation } from '@react-navigation/native';
import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Image, FlatList } from 'react-native';
import { SelectList } from 'react-native-dropdown-select-list';
import api from '../core/Service';
import axios from "axios";
import { useSelector } from 'react-redux';

const SearchItem = () => {
    const navigation = useNavigation();
    const token = useSelector(state => state.app.token);
    const [itemList, SetItemList] = useState()
    const [itemName, SetItemName] = useState("");

    const [selectedCat, setSelectedCat] = React.useState("");
    const [selectedSor, setSelectedSor] = React.useState("");
    
    const [isChecked, setIsChecked] = useState(false);
    const handleCheck = () => {
        setIsChecked(!isChecked);
    };
    const [isChecked1, setIsChecked1] = useState(false);
    const handleCheck1 = () => {
        setIsChecked1(!isChecked1);
    };
    const [isChecked2, setIsChecked2] = useState(false);
    const handleCheck2 = () => {
        setIsChecked2(!isChecked2);
    };

    const [isChecked3, setIsChecked3] = useState(false);
    const handleCheck3 = () => {
        setIsChecked3(!isChecked3);
    };

    const data = [
        { key: '1', value: 'Food/Drink' },
        { key: '2', value: 'Electrical' },
        { key: '3', value: 'Fruit & Veg' },
        { key: '4', value: 'Dairy, Eggs & Fridge'},
        { key: '5', value: 'Drinks' },
        { key: '6', value: 'Freezer' },
        { key: '7', value: 'Liquor' },
        { key: '8', value: 'Meat, Seafood & Deli' },
    ]

    const data1 = [
        { key: '1', value: 'Name A to Z' },
        { key: '2', value: 'Name Z to A' },
        { key: '3', value: 'Price low to high' },
        { key: '4', value: 'Price high to low' },
        
        
    ]

    const getItem = async () => {
        const headers = { 'Authorization': 'Bearer ' + token }
        const postobj = { name: itemName, checkWool: isChecked1, checkCol: isChecked2, checkSale: isChecked, selectCat: selectedCat, selectSor: selectedSor }
        await axios.post(`${api}/item/searchFilter`, postobj, { headers: headers })
            .then(function (response) {
                if (response) {
                    SetItemList(response?.data);
                }
            })
            .catch(function (error) {
                console.warn("ERROR: " + error);
            })
    }

    const renderItem = ({ item }) => (
        // If no discount show first display, no styles for discount/ price
        item.IP_ITEM_DISCOUNT_PCT == '0.00' || item.IP_ITEM_DISCOUNT_PCT == null ?

            <TouchableOpacity style={styles.item} onPress={() => {
                navigation.navigate('ItemInfo', {
                    id: item.ITEM_ID,
                    name: item.ITEM_NAME,
                    image: item.IMAGE,
                    price: item.IP_FOUR_WK_HIGHEST_PRICE,
                    discount: item.IP_ITEM_BASE_PRICE,
                    percent: item.IP_ITEM_DISCOUNT_PCT,
                    catagory: item.CAT_NAME,
                    company: item.COM_NAME,
                    description: item.ITEM_DESC
                })
            }}>
                <Image style={styles.image_container} source={{ uri: `${item.IMAGE}` }} />
                <View style={{ width: '100%' }}>
                    <Text style={{ fontWeight: 'bold', width: '80%' }}>{item.ITEM_NAME}</Text>
                    <View style={{ flexDirection: "row" }}>
                        <Text>$ {item.IP_FOUR_WK_HIGHEST_PRICE}</Text>
                        {item.IP_ITEM_DISCOUNT_PRICE > 0 ? <Text style={{ marginLeft: 10 }}>Discounted Price: {item.IP_ITEM_BASE_PRICE}</Text> : <Text></Text>}
                    </View>
                    <View style={{ flexDirection: 'row' }}>
                        <Text>{item.CAT_NAME ? item.CAT_NAME : "NO CATEGORY"}</Text>
                        <Text style={{ marginLeft: 50 }}>{item.COM_NAME}</Text>
                    </View>
                </View>
            </TouchableOpacity >

            :
            //  else display colour styled discounts and price
            <TouchableOpacity style={styles.item} onPress={() => {
                navigation.navigate('ItemInfo', {
                    id: item.ITEM_ID,
                    name: item.ITEM_NAME,
                    image: item.IMAGE,
                    price: item.IP_FOUR_WK_HIGHEST_PRICE,
                    discount: item.IP_ITEM_BASE_PRICE,
                    percent: item.IP_ITEM_DISCOUNT_PCT,
                    catagory: item.CAT_NAME,
                    company: item.COM_NAME,
                    description: item.ITEM_DESC
                })
            }}>
                <Image style={styles.image_container} source={{ uri: `${item.IMAGE}` }} />
                <View style={{ width: '100%' }}>
                    <Text style={{ fontWeight: 'bold', width: '80%' }}>{item.ITEM_NAME}</Text>
                    <View style={{ flexDirection: "row" }}>
                        <Text style={{ textDecorationLine: "line-through" }}>${item.IP_FOUR_WK_HIGHEST_PRICE}</Text>
                        <Text style={{ marginLeft: 5, fontWeight: 'bold', color: 'green' }}>${item.IP_ITEM_BASE_PRICE}</Text>
                        <Text style={{ marginLeft: 5, color: 'red' }}>SAVE {(item.IP_ITEM_DISCOUNT_PCT * 100).toFixed(0)}%</Text>
                    </View>
                    <View style={{ flexDirection: 'row' }}>
                        <Text>{item.CAT_NAME ? item.CAT_NAME : "NO CATEGORY"}</Text>
                        <Text style={{ marginLeft: 50 }}>{item.COM_NAME}</Text>
                    </View>
                </View>
            </TouchableOpacity>
        // end if statement for search colour display
    );
    

    return (
        <View>
            <View>
                <TouchableOpacity onPress={() => getItem()}>
                    <View style={{ flexDirection: 'row' }}>
                        <TextInput placeholder='Item name' style={styles.input_box} onChangeText={SetItemName} />
                        <TouchableOpacity style={styles.btn} onPress={() => getItem()}>
                            <Text style={styles.btn_text}>Find</Text>
                        </TouchableOpacity>
                    </View>
                </TouchableOpacity>
            </View>
            <View>
                <Text style={styles.title}>Store</Text>
                <View style={{ flexDirection: 'row' }}>
                    <TouchableOpacity onPress={handleCheck1}>
                        <View style={styles.container}>
                            <View style={{ flexDirection: 'row' }}>
                                <View style={[styles.checkbox, isChecked1 && styles.checkboxChecked]} />
                                <Text style={styles.label}>Woolworths</Text>
                            </View>
                        </View>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={handleCheck2}>
                        <View style={styles.container}>
                            <View style={{ flexDirection: 'row' }}>
                                <View style={[styles.checkbox, isChecked2 && styles.checkboxChecked]} />
                                <Text style={styles.label}>Coles</Text>
                            </View>
                        </View>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={handleCheck}>
                        <View style={styles.container}>
                            <View style={{ flexDirection: 'row' }}>
                                <View style={[styles.checkboxSale, isChecked && styles.checkboxChecked]} />
                                <Text style={styles.label}>Sale</Text>
                            </View>
                        </View>
                    </TouchableOpacity>
                </View>
            </View>
            <View style={styles.container}>
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                    <Text>Category:</Text>
                    <View style={{ flex: 1 }}>
                        <SelectList
                            dropdownStyles={{
                                backgroundColor: "white",
                                position: "absolute",
                                top: 40,
                                height: 150,
                                width: "90%",
                                zIndex: 999,
                            }}    
                            setSelected={(val) => {
                                console.log('Selected Option cat:', val);
                                setSelectedCat(val)
                            }}
                            data={data}
                            save="key"
                        />
                    </View>
                    <Text>Sort by:</Text>
                    <View style={{ flex: 1 }}>
                        <SelectList
                            defaultText='Select option...'
                            dropdownStyles={{
                                backgroundColor: "white",
                                position: "absolute",
                                top: 40,
                                height: 150,
                                width: "90%",
                                zIndex: 999,
                            }}
                            setSelected={(val) => setSelectedSor(val)}
                            data={data1}
                            save="key"
                        />
                    </View>
                </View>
            </View>
            <View style={{ backgroundColor: '#E5E5E5', height: '100%' }}>
                <View style={{ padding: 20 }}>
                    <FlatList
                        initialNumToRender={7}
                        data={itemList}
                        renderItem={renderItem}
                        showsVerticalScrollIndicator={true}
                    />
                </View>
            </View>
        </View>
    )
}



const styles = StyleSheet.create({
    container: {
        marginTop: 17,
        marginLeft:8,
        justifyContent: "center"
    },
    header: {
        fontSize: 24,
        fontWeight: 'bold',
        color: 'black'
    },
    info: {
        fontSize: 20,
        fontWeight: 'bold',
        color: 'black'
    },
    btn: {
        backgroundColor: '#4F44D0',
        width: '15%',
        height: 40,
        borderRadius: 50,
        borderBottomLeftRadius: 0,
        borderTopLeftRadius: 0
    },
    title: {
        fontSize: 20,
        fontWeight: 'bold',
        margin: 5,
        marginLeft: 8
    },
    label: {
        fontSize: 15,
        fontWeight: 'bold'
    },

    checkbox: {
        width: 16,
        height: 16,
        borderRadius: 4,
        borderWidth: 2,
        borderColor: 'black',
        marginRight: 10
    },
    checkboxSale: {
        width: 16,
        height: 16,
        borderRadius: 4,
        borderWidth: 2,
        borderColor: 'black',
        marginRight: 10,
        marginLeft: 120
    },
    checkboxChecked: {
        backgroundColor: 'green',
        borderColor: 'green'
    },
    btn1: {
        backgroundColor: 'white',
        width: '35%',
        height: 40,
        borderRadius: 0,
        borderBottomLeftRadius: 0,
        borderTopLeftRadius: 0,
        marginBottom: 8,
        marginLeft: 8
    },
    btn2: {
        backgroundColor: 'white',
        width: '35%',
        height: 40,
        borderRadius: 0,
        borderBottomLeftRadius: 0,
        borderTopLeftRadius: 0,
        marginBottom: 8,
        marginLeft: 8
    },
    btn_text: {
        fontSize: 20,
        color: 'white',
        margin: 5,
        marginLeft: 8
    },
    btn_text1: {
        fontSize: 15,
        color: 'black',
        margin: 5,
        marginLeft: 8
    },
    SelectList: {
        backgroundColor: 'red',
        height: 50, // set a fixed height for the picker
        width: '100%',
    },
    item: {
        marginVertical: 5,
        padding: 5,
        flexDirection: 'row',
        alignItems: 'center',
        borderRadius: 4,
        shadowOpacity: 0.27,
        shadowColor: 'black',
        shadowOffset: { width: 0, height: 3 },
        shadowRadius: 4.65,
        elevation: 3,
        backgroundColor: 'white'
    },
    image_container: {
        width: 72,
        height: 72,
        backgroundColor: '#6B7DDA',
        borderRadius: 4,
        marginLeft: 5
    },
    image_Icon: {
        width: 50,
        height: 50,
        backgroundColor: '#6B7DDA',
        borderRadius: 4,
        marginLeft: 50
    },
    input_box: {
        borderWidth: 2,
        borderRadius: 50,
        borderBottomRightRadius: 0,
        borderTopRightRadius: 0,
        fontSize: 20,
        height: 40,
        textAlignVertical: 'center',
        width: '80%',
        paddingHorizontal: 10,
        marginLeft: 5
    }
}) 

export default SearchItem;