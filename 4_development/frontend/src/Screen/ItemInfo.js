import { useRoute } from '@react-navigation/native';
import React from 'react';
import { SafeAreaView, Text, StyleSheet, View, Image, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';

const ItemInfo = () => {
    const navigation = useNavigation();
    const route = useRoute();
    const { id, name, image, price, discount, percent, catagory, company, description } = route.params;

    return (
        <SafeAreaView>
            <Image style={styles.image_container} source={{ uri: `${image}` }} />
            <View style={styles.container}>
                <View style={{ width: '100%' }}>
                    <Text style={styles.item_name}>{name}</Text>
                    <View style={{ flexDirection: "row", marginTop: 10 }}>
                        <Text style={styles.item_price}>Price: </Text>
                        {discount < price ? <Text style={styles.item_slashed_price}>${price}</Text> : <Text style={styles.item_price}>${price}</Text>}
                        {discount < price ? <Text style={styles.item_discount_price}>${discount}</Text> : <Text></Text>}
                        {discount < price ? <Text style={styles.item_discount_percentage}>SAVE {percent * 100}%</Text> : <Text></Text>}
                    </View>
                    <View style={{ flexDirection: 'row' }}>
                        <Text style={styles.item_catcom}>Category: {catagory ? catagory : "NO CATEGORY"}</Text>
                        <Text style={styles.item_catcom}>   Shop: {company}</Text>
                    </View>
                    <View>
                        <Text style={styles.item_description}>{description ? description : "No description for this item."}</Text>
                    </View>
                </View>
            </View>
            <View>
                <TouchableOpacity style={styles.btn} onPress={() => navigation.navigate('PriceHistory', {id : id})}>
                    <Text style={styles.btn_text}>Price History</Text>
               </TouchableOpacity>
            </View>
        </SafeAreaView>
    )
}

const styles = StyleSheet.create({
    container: { marginLeft: '10%' },
    image_container: {
        width: 128,
        height: 128,
        backgroundColor: '#6B7DDA',
        alignSelf: 'center',
        margin: 10
    },
    item_name: {
        fontWeight: 'bold',
        width: '80%',
        fontSize: 20
    },
    item_price: {
        fontWeight: 'bold',
        fontSize: 20,
        color: '#555555'
    },
    item_slashed_price: {
        textDecorationLine: "line-through",
        fontWeight: 'bold',
        fontSize: 20
    },
    item_discount_price: {
        marginLeft: 15,
        fontWeight: 'bold',
        color: 'green',
        fontSize: 20
    },
    item_discount_percentage: {
        marginLeft: 15,
        color: 'red',
        fontSize: 20
    },
    item_description: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#555555',
        marginTop: 10
    },
    item_catcom: {
        fontSize: 16
    },
    btn: {
        backgroundColor: '#4F44D0',
        width: '30%',
        height: 35,
        borderRadius: 0,
        borderBottomLeftRadius: 0,
        borderTopLeftRadius: 0,
        marginTop: 30,
        alignSelf: 'center'
    },
    btn_text: {
        fontSize: 16,
        color: 'white',
        margin: 5,
        textAlign: 'center',
        verticalAlign: 'middle'
    }
})

export default ItemInfo;