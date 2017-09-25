# -*- coding: utf-8 -*-
import scrapy
import json

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
		producto = response.selector.xpath('.//script[@type="application/json"]/text()').extract_first()
		producto = producto.strip()
		producto = json.loads(producto)
		item = {
			'id': producto.get('id'),
			'nombre': producto.get('title'),
			'precio': producto.get('price') / 100,
			'imagenes': producto.get('images'),
			'descripcion': producto.get('content'),
			'marca': producto.get('vendor')
		}
		yield item
