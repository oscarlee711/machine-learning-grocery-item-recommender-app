//get MySQL db
const db = require('../util/database');

//model for the item table
module.exports = class item {
	constructor(item_id, cat_id, item_name, item_price, item_measurement, item_unit, item_unit_price, item_image_id, item_desc) {
        this.item_id = item_id;
        this.cat_id = cat_id;
        this.item_name = item_name;
		this.item_price = item_price;
		this.item_measurement = item_measurement;
		this.item_unit = item_unit;
		this.item_unit_price = item_unit_price;
		this.item_image_id = item_image_id;
        this.item_desc = item_desc;
    }

    //db test
    static fetchAll() {
        return db.execute('SELECT * FROM ITEM limit 10');
    }

    static getRecommended(id) {
        return db.execute('SELECT i.ITEM_ID,i.ITEM_NAME,i.ITEM_DESC,pcr.IP_FOUR_WK_HIGHEST_PRICE,pcr.IP_ITEM_BASE_PRICE,pcr.IP_ITEM_DISCOUNT_PCT,cat.CAT_NAME,c.COM_NAME,im.IMAGE from RECOMMEND_ITEM r inner join ITEM i on r.ITEM_ID = i.ITEM_ID inner join ITEM_PRICE_CURRENT pcr on pcr.ITEM_ID = i.ITEM_ID inner join CATEGORY cat on i.CAT_ID = cat.CAT_ID inner join COMPANY c on r.COM_ID = c.COM_ID inner join ITEM_IMAGE im on i.ITEM_IMAGE_ID = im.ITEM_IMAGE_ID where r.USER_ID = ? ORDER BY IP_ITEM_DISCOUNT_PCT DESC limit 0,10', [id]);
    }

    //search for items by name
    static searchItem(name) {
        return db.execute('SELECT * FROM ITEM WHERE name = ?', [name]);
    }
	
	static searchItemFilter(name, checkWool, checkCol, checkAld, checkSale, selectCat, selectSor) {

        var isSale = ''
        if (checkSale == true) {
            isSale = ' IP_ITEM_DISCOUNT_PCT != "0" and'
        } 


        var woolworths = ''
        if (checkWool == true) {
            woolworths = ' COMPANY.COM_ID = "1" and'
        } 

        var coles = ''
        if (checkCol == true) {
            coles = ' COMPANY.COM_ID = "2" and'
        }

        var aldi = ''
        if (checkAld == true) {
            aldi = ' COMPANY.COM_ID = "3" and'
        }


        var cat = ''
        if (selectCat != 0) {
            cat = ' ITEM.CAT_ID = "' + selectCat + '" and'
        } else {
            cat = ' ITEM.CAT_ID != "0" and'
        }

        var sort = ''
        if (selectSor == 1) {
            sort = ' order by ITEM_NAME asc'
        } else if (selectSor ==  2) {
            sort = ' order by ITEM_NAME desc'
        } else if (selectSor == 3) {
            sort = ' order by IP_FOUR_WK_HIGHEST_PRICE asc'
        } else if (selectSor == 4) {
            sort = ' order by IP_FOUR_WK_HIGHEST_PRICE desc'
        }


        return db.execute('SELECT ITEM.ITEM_NAME, ITEM.ITEM_DESC, ITEM_IMAGE.IMAGE, IP_ITEM_BASE_PRICE, IP_FOUR_WK_HIGHEST_PRICE, IP_ITEM_DISCOUNT_PCT, IP_ITEM_DISCOUNT_PRICE, CATEGORY.CAT_NAME, COMPANY.COM_NAME ' +
            ' FROM ITEM inner join ITEM_PRICE_CURRENT on ITEM.ITEM_ID = ITEM_PRICE_CURRENT.ITEM_ID ' +
            ' left outer join ITEM_IMAGE on ITEM.ITEM_IMAGE_ID = ITEM_IMAGE.ITEM_IMAGE_ID ' +
            ' inner join CATEGORY on ITEM.CAT_ID = CATEGORY.CAT_ID' +
            ' inner join COMPANY on ITEM_PRICE_CURRENT.COM_ID = COMPANY.COM_ID where' +
            cat +
            woolworths +
            coles +
            aldi +
            isSale +
            ' ITEM_NAME LIKE ?' +
            sort +
            ' limit 100 ', ['%' + name + '%']);
            
           
    }

    /*static searchItemFilter(name) {
        return db.execute('SELECT ITEM.ITEM_NAME, ITEM.ITEM_DESC, ITEM_IMAGE.IMAGE, IP_ITEM_BASE_PRICE, IP_FOUR_WK_HIGHEST_PRICE, IP_ITEM_DISCOUNT_PCT, IP_ITEM_DISCOUNT_PRICE, CATEGORY.CAT_NAME, COMPANY.COM_NAME ' +
            ' FROM ITEM inner join ITEM_PRICE_CURRENT on ITEM.ITEM_ID = ITEM_PRICE_CURRENT.ITEM_ID ' +
            ' left outer join ITEM_IMAGE on ITEM.ITEM_IMAGE_ID = ITEM_IMAGE.ITEM_IMAGE_ID ' +
            ' inner join CATEGORY on ITEM.CAT_ID = CATEGORY.CAT_ID' +
            ' inner join COMPANY on ITEM_PRICE_CURRENT.COM_ID = COMPANY.COM_ID' +
            ' where ITEM_NAME LIKE ? limit 100', ['%' + name + '%']);
    }*/

    static searchInvoiceHistory(dateVal, id) { // Alteration can be avoided
        return db.execute('Select STORE.STORE_NAME, CATEGORY.CAT_NAME, ORDER_ITEM_BASE_PRICE, ORDER_ITEM_QTY, ORDER_ITEM_DISCOUNT_PRICE, ' +
            ' ITEM.ITEM_NAME, USER_ORDER.ORDER_TOTAL_PRICE, ORDER_TOTAL_DISCOUNT , ORDER_DTTM, ITEM_IMAGE.IMAGE ' +
            ' from ORDER_ITEM inner join ITEM on ORDER_ITEM.ITEM_ID = ITEM.ITEM_ID ' +
            ' inner join USER_ORDER on ORDER_ITEM.ORDER_ID = USER_ORDER.ORDER_ID ' +
            ' inner join USER on USER_ORDER.USER_ID = USER.USER_ID ' +
            ' inner join CATEGORY on CATEGORY.CAT_ID = ITEM.CAT_ID ' +
            ' inner join STORE on STORE.STORE_ID = USER_ORDER.STORE_ID  inner join ITEM_IMAGE on ITEM_IMAGE.ITEM_IMAGE_ID = ITEM.ITEM_IMAGE_ID ' +
            ' where USER_ORDER.ORDER_DTTM > ? and USER.USER_ID = ?' +
            ' order by USER_ORDER.ORDER_DTTM desc ', [dateVal, id]);
    }

	// item_id,cat_id,item_name,item_price,item_measurement,item_unit,item_unit_price,item_image_id,item_desc
	
    //post item
    static post(item_id, cat_id, item_name, item_price, item_measurement, item_unit, item_unit_price, item_image_id, item_desc) {
        return db.execute('INSERT INTO ITEM (ITEM_ID, CAT_ID, ITEM_NAME, ITEM_PRICE, ITEM_MEASUREMENT, ITEM_UNIT, ITEM_UNIT_PRICE, ITEM_IMAGE_ID, ITEM_DESC) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', [item_id, cat_id, item_name, item_price, item_measurement, item_unit, item_unit_price, item_image_id, item_desc]);
    }

    //change item
    static put(cat_id, item_name, item_price, item_measurement, item_unit, item_unit_price, item_image_id, item_desc, item_id) {
        return db.execute('UPDATE ITEM SET CAT_ID = ?, ITEM_NAME = ?, ITEM_PRICE = ?, ITEM_MEASUREMENT = ?, ITEM_UNIT = ?, ITEM_UNIT_PRICE = ?, ITEM_IMAGE_ID = ?, ITEM_DESC = ? WHERE ITEM_ID = ?', [cat_id, item_name, item_price, item_measurement, item_unit, item_unit_price, item_image_id, item_desc, item_id])
    }
}