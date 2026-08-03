import sqlite3
import pandas as pd
import os
import sys
from collections import defaultdict
import math
import re

class npiFileHelper:
    # record is array of tuples 
# returns table it was published in 
    def __init__(self):
        self.npi_table = ["NPI", "Entity_Type_Code", "Replacement_NPI", "Employer_Identification_Number__EIN_"]
        self.provider_table = ["Provider_Organization_Name__Legal_Business_Name_", "Provider_Last_Name__Legal_Name_", 
                              "Provider_First_Name", "Provider_Middle_Name", "Provider_Name_Prefix_Text",
                              "Provider_Name_Suffix_Text", "Provider_Credential_Text", "Provider_Other_Organization_Name",
                              "Provider_Other_Organization_Name_Type_Code", "Provider_Other_Last_Name", 
                              "Provider_Other_First_Name", "Provider_Other_Middle_Name", "Provider_Other_Name_Prefix_Text",
                              "Provider_Other_Name_Suffix_Text", "Provider_Other_Credential_Text"]
        self.taxonomy_table = ["Healthcare_Provider_Taxonomy_Code", "Provider_License_Number", "Provider_License_Number_State_Code", "Healthcare_Provider_Primary_Taxonomy_Switch"]
        self.other_provider_table = ["Other_Provider_Identifier", "Other_Provider_Identifier_State", "Other_Provider_Identifier_Issuer"]
        self.healthcare_provider_taxonomy_table = ["Healthcare_Provider_Taxonomy_Group"]
        self.address_table = ["Provider_First_Line_Business_Mailing_Address", "Provider_Second_Line_Business_Mailing_Address",
                              "Provider_Business_Mailing_Address_City_Name", "Provider_Business_Mailing_Address_State_Name",
                              "Provider_Business_Mailing_Address_Postal_Code", "Provider_Business_Mailing_Address_Country_Code__If_outside_US_",
                              "Provider_Business_Mailing_Address_Telephone_Number", "Provider_Business_Mailing_Address_Fax_Number",
                              "Provider_First_Line_Business_Practice_Location_Address", "Provider_Second_Line_Business_Practice_Location_Address",
                              "Provider_Business_Practice_Location_Address_City_Name", "Provider_Business_Practice_Location_Address_State_Name",
                              "Provider_Business_Practice_Location_Address_Postal_Code", "Provider_Business_Practice_Location_Address_Country_Code__If_outside_US_",
                              "Provider_Business_Practice_Location_Address_Telephone_Number", "Provider_Business_Practice_Location_Address_Fax_Number"]
        self.enumeration_deactivation_reactivation_table = ["Provider_Enumeration_Date", "Last_Update_Date", "NPI_Deactivation_Reason_Code",
                                                            "NPI_Deactivation_Date", "NPI_Reactivation_Date", "Certification_Date"]
        self.parentorg = ["Is_Sole_Proprietor", "Is_Organization_Subpart", "Parent_Organization_LBN", "Parent_Organization_TIN",
                          "Authorized_Official_Name_Prefix_Text", "Authorized_Official_Name_Suffix_Text", "Authorized_Official_Credential_Text"]
        self.sex_name_official_table = ["Provider_Sex_Code", "Authorized_Official_Last_Name", "Authorized_Official_First_Name",
                                        "Authorized_Official_Middle_Name", "Authorized_Official_Title_or_Position",
                                        "Authorized_Official_Telephone_Number"]
        self.tables = [self.npi_table, self.provider_table, self.taxonomy_table, self.other_provider_table, 
                       self.healthcare_provider_taxonomy_table, self.address_table,
                       self.enumeration_deactivation_reactivation_table, self.parentorg,
                       self.sex_name_official_table]

    def findNameFromArray(self, table_array):
        if table_array == self.npi_table:
            return "NPI_Table", 1
        if table_array == self.provider_table:
            return "Provider_Name", 1
        if table_array == self.taxonomy_table:
            return "Taxonomy_Table", 2
        if table_array == self.other_provider_table:
            return "Other_Provider_Name", 1
        if table_array == self.healthcare_provider_taxonomy_table:
            return "Healthcare_Provider_Taxonomy_Group", 2
        if table_array == self.address_table:
            return "Address_Information", 1
        if table_array == self.enumeration_deactivation_reactivation_table:
            return "Enumeration_Deactivation_Reactivation_Dates", 1
        if table_array == self.parentorg:
            return "Parent_Organizations", 1
        if table_array == self.sex_name_official_table:
            return "Official_Name_And_Sex", 1
        return "Error"

    def getTable(self, column):
        if column in self.npi_table:
            return "NPI_Table"
        if column in self.provider_table:
            return "Provider_Name"
        if column in self.taxonomy_table:
            return "Taxonomy_Table"
        if column in self.other_provider_table:
            return "Other_Provider_Name"
        if column in self.healthcare_provider_taxonomy_table:
            return "Healthcare_Provider_Taxonomy_Group"
        if column in self.address_table:
            return "Address_Information"
        if column in self.enumeration_deactivation_reactivation_table:
            return "Enumeration_Deactivation_Reactivation_Dates"
        if column in self.parentorg:
            return "Parent_Organizations"
        if column in self.sex_name_official_table:
            return "Official_Name_And_Sex"
        return "Error"
    
#next step: if field in some table, do this. if not in any table, return False 
    def publishRowNPI(self, NPI, field, entry, updatedRecord):
        #NPI is type array

        update = defaultdict(list)
        
        for table in self.tables:
            if field in table:
                print(f'''field is {field} in table {table}''')
                table_name, code = self.findNameFromArray(table)
                print(f'''table name is {table_name}''')

                #print(f'''entry {entry}''')
                #EDIT: need to return a list of tuples here instead of this. ******
                updatedRecordList = []
                for item in entry:
                    updatedRecordList.append((table_name, self.publishRowNPIHelper(code, NPI, field, item, updatedRecord)))
                    #might need to separate based on code to get correct id
                return updatedRecordList

    def publishRowNPIHelper(self, code, NPI, field, item, updatedRecord):
        if code == 1:
            return self.publishRowNPIHelper1(NPI, field, item, updatedRecord)
        if code == 2:
            return self.publishRowNPIHelper2(NPI, field, item, updatedRecord)

    def publishRowNPIHelper1(self, NPI, field, item, updatedRecord):
        
        updatedRecord[field] = item[0]
        updatedRecord["NPI"] = NPI[0]

        #print(f''' updated record is {updatedRecord}''')
        return updatedRecord


# if the number needs to be parsed out to create an id
    def publishRowNPIHelper2(self, NPI, field, item, updatedRecord):
        updatedRecord[field] = item[0]
        updatedRecord["_id"] = str(NPI[0]) + "." + str(item[1])
        updatedRecord["NPI"] = NPI[0]

        #print(f''' updated record is {updatedRecord}''')
        return updatedRecord
