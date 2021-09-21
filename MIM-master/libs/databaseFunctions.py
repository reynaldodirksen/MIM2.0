import mysql.connector
# import scriptreadprod as products
mydb = mysql.connector.connect(
    host = "192.168.12.10",
    port = "3307",
    user = "SUAM",
    password = "Maria!1007",
    database = "SUAM"
    )
mycursor = mydb.cursor()

def returnOrders():
    
    mycursor.execute('SELECT  `Name` FROM `Orders` WHERE state = 3 ORDER BY `Orders`.`Name` ASC')
    myresult = mycursor.fetchall()
    MO = [0 for i in range(len(myresult))]
    for i in range(len(myresult)):
        MO[i] = myresult[i][0]
    return MO

def returnOperators():
    mycursor.execute("Select Name from Operators ORDER BY `Operators`.`Name` ASC")
    myresult = mycursor.fetchall()
    operators = [0 for i in range(len(myresult))]
    for i in range(len(myresult)):
        operators[i] = myresult[i][0]
    return operators

def returnProductInfo(order):
    query = "select * from Products where ID = (Select ProductID from Orders where Name = %s)"
    val = (order, )
    mycursor.execute(query, val)
    myresult = mycursor.fetchall()[0]
    return myresult

def returnOrderInfo(order):
    query = "Select * from Orders where Name = %s"
    val = (order, )
    mycursor.execute(query, val)
    myresult = mycursor.fetchall()[0]
    return myresult

def returnVPSW(product):
    query = "Select VPSW from PlateSetup where ID =  (Select SensorPlateID from Products where Name = %s)"
    val = (product, )
    mycursor.execute(query, val)
    myresult = mycursor.fetchone()[0]
    print(myresult)
    return myresult

def exportSensor(version, sensorid):
    query = "SELECT ID FROM `Sensors` WHERE `HAL_ID` = %s"
    val = (sensorid,)
    mycursor.execute(query, val)
    myresult = mycursor.fetchone()
    if myresult == None:
        query = "INSERT INTO `Sensors`( `HAL_ID`, `Type`) VALUES (%s, %s)"
        val = (sensorid, version)
        mycursor.execute(query, val)
        mydb.commit()
    
    
def exportValues(sensorid, stationID, operator, order, tc, tcsq, MR,sensitivity, offset, vps, sens, ZTV):
    MR = 20*(MR+1)
    vps = round(vps, 4)
    query = "INSERT INTO `Setups`(`SensorID`, `StationID`, `OperatorID`, `OrderID`, `TC`, `TCSQ`, `MRange`, `Sensitivity`, `Offset`, `VPS`, `vpsSensitivity`, `ZTV`) VALUES ((select ID from Sensors where HAL_ID = %s), %s, (Select ID from Operators where Name = %s), (Select ID from Orders where Name = %s), %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (sensorid, stationID, operator, order, tc, tcsq, MR,sensitivity, offset, vps, sens, ZTV)
    mycursor.execute(query, val)
    mydb.commit()
    
    
def addIncident(stationID, operator, order, hal_id, error, version):
    print(stationID, operator, order, hal_id, error, version)
    query = "INSERT INTO `Incidents`(`StationID`, `OperatorID`, `OrderID`, `HAL_ID`, `Error`, `SW_version`) VALUES (%s, (Select ID from Operators where Name = %s), (Select ID from Orders where Name = %s), %s, %s, %s)"
    val =(stationID, operator, order, hal_id, error, version) 
    mycursor.execute(query, val)
    mydb.commit()