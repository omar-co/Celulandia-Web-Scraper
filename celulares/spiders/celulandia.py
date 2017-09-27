# -*- coding: utf-8 -*-
import scrapy
import json
from collections import namedtuple


class CelulandiaSpider(scrapy.Spider):
    name = "celulandia"
    base_url = 'https://celulandia.com.mx'
    start_urls = ['https://celulandia.com.mx/collections/all']

    def parse(self, response):
        products = response.css('div.product-index')
        if (products):
            for product in products:
                if (not product.css('div.so')):
                    product_url = self.base_url + product.css('div.product-info a::attr(href)').extract_first()
                    yield scrapy.Request(product_url, callback=self.parse_details)

        next_page_url = response.selector.xpath('.//link[@rel="next"]/@href').extract_first()
        if (next_page_url):
            next_page_url = self.base_url + next_page_url
            yield scrapy.Request(next_page_url, self.parse)

    def parse_details(self, response):
        producto = response.css('form.product_form::attr(data-product)').extract_first()
        producto = producto.strip()
        producto = json.loads(producto, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

        stock = 0
        options = []
        for p in producto.variants:
            stock += p.inventory_quantity
            self.quantity += stock
            options += p.options
        self.total += (producto.price * stock) / 100

        item = {
            'id': producto.id,
            'nombre': producto.title,
            'precio': producto.price / 100,
            'marca': producto.vendor,
            'stock': stock,
            'variantes': options,
            'etiquetas': producto.tags,
            'imagenes': producto.images,
            'descripcion': producto.content
        }
        yield item
