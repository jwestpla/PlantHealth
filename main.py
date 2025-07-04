import API
import webScraping
import extractFromPdfs
import createJSON
#import FTP_uploading

def main():
    print("Running API script...")
    API.run()

    print("Running Web Scraping script...")
    webScraping.run()

    print("Running Extract From PDFs script...")
    extractFromPdfs.run()

    print("Running Create JSON script...")
    createJSON.run()

# Not using the upload script anymore since github actions will do it for me so i do not leak passwords and such    
    # print("Running FTP_uploading script...")
    # FTP_uploading.run()


    
if __name__ == '__main__':
    main()
    
