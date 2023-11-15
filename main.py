# StudentID: 001454573

import csv
import datetime

# Load address and distance data from CSV files
with open("csvs/address.csv") as addressFile:
    addressData = csv.reader(addressFile)
    addressData = list(addressData)

with open("csvs/distance.csv") as distanceFile:
    distanceData = csv.reader(distanceFile)
    distanceData = list(distanceData)   

# Hash table class for storing and managing package data
class HashTableWChains:
    def __init__(self, initialCapacity=40):
        # Initialize hash table with empty lists
        self.table = []
        for i in range(initialCapacity):
            self.table.append([])

    # Insert or update an item in the hash table
    def insert(self, key, item):
        bucket = hash(key) % len(self.table)
        bucketList = self.table[bucket]
        
        for keyValue in bucketList:
            if keyValue[0] == key:
                keyValue[1] = item
                return True    
        keyValue = [key, item]
        bucketList.append(keyValue)
        return True

    # Search for an item by key
    def search(self, key):
        bucket = hash(key) % len(self.table)
        bucketList = self.table[bucket]
        for keyValue in bucketList:
            if keyValue[0] == key:
                return keyValue[1]
        return None 
        
    # Remove an item by key
    def remove(self, key):
        bucket = hash(key) % len(self.table)
        bucketList = self.table[bucket]
        if key in bucketList:
            bucketList.remove(key)
    
# Class representing a package
class Package:
    def __init__(self, id, street, city, state, zipCode, deadline, weight, notes, status, departureTime, deliveryTime,instructions,truckNumber=None):
        self.id = id
        self.street = street
        self.city = city
        self.state = state
        self.zipCode = zipCode
        self.deadline = deadline
        self.weight = weight
        self.notes = notes
        self.status = status
        self.instructions = instructions
        self.departureTime = None 
        self.deliveryTime = None
        self.truckNumber = truckNumber

    def __str__(self):
        # Only include delivery time in the string if the package status is 'Delivered'
        deliveryTimeStr = self.deliveryTime if self.status == "Delivered" else "N/A"
        truckNumberStr = f"Truck {self.truckNumber}" if self.truckNumber is not None else "Not assigned"
        return (
            f"ID: {self.id}, "
            f"Address: {self.street}, {self.city}, {self.state}, {self.zipCode}, "
            f"Deadline: {self.deadline}, "
            f"Weight: {self.weight}, "
            f"Status: {self.status}, "
            f"Departure Time: {self.departureTime}, "
            f"Delivery Time: {deliveryTimeStr}, "
            f"Assigned to: {truckNumberStr}"
        )

    # Update the status of a package based on the current time
    def statusUpdate(self, currentTime):
        if self.deliveryTime == None:
            self.status = "At the hub"
        elif currentTime < self.departureTime:
            self.status = "At the hub"   
        elif currentTime < self.deliveryTime:
            self.status = "En route"     
        else:
            self.status = "Delivered" 
        # Special case for package with ID 9
        if self.id == 9:
            if currentTime > datetime.timedelta(hours=10, minutes=20):
                self.street = "410 S State St"  
                self.zipCode = "84111"  
            else:
                self.street = "300 State St"
                self.zipCode = "84103"   

# Global lists to store package IDs for each truck
truck1_packages = []
truck2_packages = []
truck3_packages = []

def assignPackageToTruck(packageId, truckNumber):
    package = packageHash.search(packageId)
    if package:
        package.truckNumber = truckNumber

# Load package data from CSV file and insert into the hash table
def loadPackageData(filename):
    with open(filename) as packageFile:
        packageInfo = csv.reader(packageFile, delimiter=',')
        next(packageInfo)  # Skip header row
        for package in packageInfo:
            packageId = int(package[0])
            packageStreet = package[1]
            packageCity = package[2]
            packageState = package[3]
            packageZip = package[4]
            packageDeadline = package[5]
            packageWeight = package[6]
            packageNotes = package[7]
            packageInstructions = package[7]
            packageStatus = "At the Hub"
            packageDepartureTime = None
            packageDeliveryTime = None

            newPackage = Package(packageId, packageStreet, packageCity, packageState, packageZip, packageDeadline, packageWeight, packageNotes, packageStatus, packageDepartureTime, packageDeliveryTime, packageInstructions)
            packageHash.insert(packageId, newPackage)

            if "Can only be on truck 2" in packageInstructions:
                truck2_packages.append(packageId)
            elif "Delayed on flight" in packageInstructions or "Wrong address listed" in packageInstructions:
                truck3_packages.append(packageId)
            else:
                truck1_packages.append(packageId)

    # Assign packages to trucks after loading all packages
    for packageId in truck1_packages:
        assignPackageToTruck(packageId, 1)
    for packageId in truck2_packages:
        assignPackageToTruck(packageId, 2)
    for packageId in truck3_packages:
        assignPackageToTruck(packageId, 3)


packageHash = HashTableWChains()

# Class representing a delivery truck
class Truck:
    def __init__(self, speed, miles, currentLocation, departTime, packages):
        self.speed = speed
        self.miles = miles
        self.currentLocation = currentLocation
        self.time = departTime
        self.departTime = departTime
        self.packages = packages

    def __str__(self):
        return "%s,%s,%s,%s,%s,%s" % (self.speed, self.miles, self.currentLocation, self.time, self.departTime, self.packages)

# Find the index of an address in the address data
def findAddressIndex(address):
    for row in addressData:
        if address in row[2]:
            return int(row[0])

# Calculate the distance between two addresses
def calculateDistance(addressIndex1, addressIndex2):
    distance = distanceData[addressIndex1][addressIndex2]
    if distance == '':
        distance = distanceData[addressIndex2][addressIndex1]
    return float(distance)

loadPackageData('csvs/package.csv')

# Initialize trucks with the package lists
truck1 = Truck(18, 0.0, "4001 South 700 East", datetime.timedelta(hours=8), truck1_packages)
truck2 = Truck(18, 0.0, "4001 South 700 East", datetime.timedelta(hours=9, minutes=5), truck2_packages)
truck3 = Truck(18, 0.0, "4001 South 700 East", datetime.timedelta(hours=11), truck3_packages)


# Function to simulate the delivery of packages by a truck
def truckDeliverPackages(truck):
    enroutePackages = [packageHash.search(packageId) for packageId in truck.packages if packageHash.search(packageId) is not None]

    truck.packages.clear()
    while enroutePackages:
        shortestDistance = float('inf')
        nextPackage = None

        for package in enroutePackages:
            currentAddressIndex = findAddressIndex(truck.currentLocation)
            packageAddressIndex = findAddressIndex(package.street)
            distanceToPackage = calculateDistance(currentAddressIndex, packageAddressIndex)

            if distanceToPackage < shortestDistance:
                shortestDistance = distanceToPackage
                nextPackage = package

        if nextPackage:
            truck.packages.append(nextPackage.id)    
            enroutePackages.remove(nextPackage)
            truck.miles += shortestDistance
            truck.currentLocation = nextPackage.street
            truck.time += datetime.timedelta(hours=shortestDistance / truck.speed)
            nextPackage.deliveryTime = truck.time
            nextPackage.departureTime = truck.departTime
    
truckDeliverPackages(truck1)
truckDeliverPackages(truck2)
truckDeliverPackages(truck3)

print("Western Governors University Parcel Service")

totalMileage = truck1.miles + truck2.miles + truck3.miles
print("Total Mileage for all trucks:", totalMileage)

# Interactive loop for user to check package status
while True:
    userInput = input("\nEnter a time (HH:MM) to view the status of each package or 'exit' to quit: ")
    if userInput.lower() == 'exit':
        break  # Exit the loop
    
    (hour, minute) = userInput.split(":")
    currentTime = datetime.timedelta(hours=int(hour), minutes=int(minute))
    
    for packageId in range(1, 41):
        package = packageHash.search(packageId)
        if package:
            package.statusUpdate(currentTime)
            print(str(package))