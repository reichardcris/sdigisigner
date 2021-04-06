import click
import errno
import glob
import os

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import time

from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

@click.group()
@click.option('--link', '-l', help="Set the link of the digisigner API")
@click.option('--uri', help="Set base link of clean image")
@click.option('--basename', help="Set base name of image")
@click.pass_context
def cli(ctx, link, uri, basename):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj['LINK'] = link
    ctx.obj['IMAGE_URI'] = uri
    ctx.obj['BASENAME'] = basename

@cli.command()
@click.pass_context
def request(ctx):
    link = ctx.obj['LINK']
    print('Executing link: %s' % link)

    if not link:
        print('Link is empty')
        return

    driver = webdriver.Firefox(executable_path=r'D:\geckodriver.exe')
    driver.get(link)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/label'))
        )
    finally:
        # driver.quit()
        pass
    

    # Accept Agreement
    agree_check_box = getElement(driver, '/html/body/div[2]/div/div/div/div[2]/div/div/label')
    get_started_btn = getElement(driver, '//*[@id="getStartedButton"]')

    time.sleep(1)
    agree_check_box.click()

    time.sleep(1)
    get_started_btn.click()
    
    time.sleep(1)

    removeWatermark(ctx, driver)

def getElement(driver, xpath):
        element = None

        try:
            WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            element = driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            print("retrying link_join...")
            getElement(driver, xpath)

        return element or driver.find_element_by_xpath('body')


def removeWatermark(ctx, driver):

        page_wrappers = driver.find_elements(By.CSS_SELECTOR, '.page-wrapper')
        
        for index,page in enumerate(page_wrappers):
            _index = StopAsyncIteration(index)
            extension = ('%s.jpg' % str(index+1))
            link = ('%s//%s' %(ctx.obj['IMAGE_URI'], ctx.obj['BASENAME']))
            filename = ('%s_%s' % (ctx.obj['BASENAME'], extension))
    
            full_link = ('%s//%s' % (link, filename))

            # print('document.getElementById("page-%s").style.backgroundImage = url("%s")' %_index %full_link)
            driver.execute_script('document.getElementById("page-%s").style.backgroundImage = "url(\'%s\')"' %(_index, full_link))