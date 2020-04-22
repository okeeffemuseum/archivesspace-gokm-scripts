from bs4 import BeautifulSoup as Soup
import csv

# This function takes an xml file from Koha and pulls the following metadata:
# 1. local control number
# 2. call numbers
# 3. barcodes
# 4. author
# 5. title

def to_csv(data_array, csv_filename):
	#specify the header fields for the csv
	fields = ["local_control_no", "call_nos", "barcodes", "author", "title"]

	# writing to csv file 
	with open(csv_filename, 'w', encoding="utf-8") as csvfile: 

		# creating a csv dict writer object 
		writer = csv.DictWriter(csvfile, fieldnames = fields) 

		# writing headers (field names) 
		writer.writeheader() 

		# writing data rows 
		writer.writerows(data_array)


def main():
	data = []

	#open file as XML
	with open(input("Path to Koha XML: ")) as fp:
		soup = Soup(fp, "xml")


	for record in soup.find_all('record'):	
		#find local control number
		local_control_no = ""
		for local_id in record.find_all('controlfield', tag="001"):
			local_control_no = local_id.get_text()
		 
		#find call numbers
		call_nos = []
		for datafield in record.find_all('datafield', tag="090"):
			for call_no in datafield.find_all('subfield', code="a"):
				call_nos.append(call_no.get_text())

		#find barcodes
		barcodes = []
		for datafield in record.find_all('datafield', tag="952"):
			for barcode in datafield.find_all('subfield', code="p"):
				barcodes.append(barcode.get_text())

		#find author
		author = ""
		for authors in record.find_all('datafield', tag="100"):
			for name in authors.find_all('subfield', code="a"):
				author = author + name.get_text()

		#find title
		title = ""
		main_title = ""
		sub_title = ""
		for titles in record.find_all('datafield', tag="245"):
			for results in titles.find_all('subfield', code="a"):
				main_title = results.get_text()
			for results in titles.find_all('subfield', code="b"):
				sub_title = results.get_text()
			title = main_title+sub_title

		#append book metadata to list
		data.append({"local_control_no":local_control_no, "call_nos":call_nos, "barcodes":barcodes, "author":author, "title":title})

	to_csv(data, "koha_parsed.csv")

if __name__ == '__main__':
	main()		