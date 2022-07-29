from django.http import JsonResponse
from django.conf import settings
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.decorators import api_view

from api.models import Blog, Brand, Category, Product, SubCategory, Video
from api.serializers import BlogSerializer, BrandSerializer, CategorySerializer, ProductSerializer, SubCategorySerializer, VideoSerializer

import csv, os
import urllib
from urllib.parse import urlparse
import urllib.request
from bs4 import BeautifulSoup
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

# Create your views here.
class Home(GenericAPIView):
    def get(self,request):
        return JsonResponse({'success' : 'success'})
        
class Videos(GenericAPIView):
    serializer_class = VideoSerializer
    queryset = Video.objects.all()

    def get(self,request, pk):
        if pk == '0':
            serializer = self.serializer_class(Video.objects.all(), many = True)
        else:
            video = Video.objects.filter(pk=pk).first()
            if video is None:
                return JsonResponse({'failure':'No such video exists'},status = status.HTTP_404_NOT_FOUND , safe = False)
            video.views += 1
            video.save()
            serializer = self.serializer_class(video)
        return JsonResponse(serializer.data, status = status.HTTP_200_OK, safe = False)

class Blogs(GenericAPIView):
    serializer_class = BlogSerializer
    queryset = Blog.objects.all()

    def get(self,request, pk):
        if pk == '0':
            serializer = self.serializer_class(Blog.objects.all(), many = True)
        else:
            obj = Blog.objects.filter(pk=pk).first()
            if obj is None:
                return JsonResponse({'failure':'No such blog exists'},status = status.HTTP_404_NOT_FOUND , safe = False)
            serializer = self.serializer_class(obj)
        return JsonResponse(serializer.data, status = status.HTTP_200_OK, safe = False)

    def post(self,request, pk):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status = status.HTTP_201_CREATED, safe = False)
        return JsonResponse(serializer.errors, status = status.HTTP_400_BAD_REQUEST , safe = False)

@api_view(['POST'])
def all_products(request):
    filter = request.data['filter']
    if len(filter) == 1:
        category = Category.objects.get(name = filter[0])
        products = Product.objects.filter(category = category).order_by('rank')
        serializer = ProductSerializer(products, many = True)
    elif len(filter) == 2:
        subcategory = SubCategory.objects.get(name = filter[1])
        products = Product.objects.filter(subcategory = subcategory).order_by('rank')
        serializer = ProductSerializer(products, many = True)
    elif len(filter) == 3:
        category = Category.objects.get(name = filter[0])
        brand = Brand.objects.filter(name = filter[2]).first()
        if brand is None:
            return JsonResponse({'failure':'No such brand exists'},status = status.HTTP_404_NOT_FOUND , safe = False)
        products = Product.objects.filter(category = category, brand = brand).order_by('rank')
        serializer = ProductSerializer(products, many = True)
    else:
        serializer = ProductSerializer(Product.objects.all().order_by('rank'), many = True)
    return JsonResponse(serializer.data, status = status.HTTP_200_OK, safe = False)

@api_view(['POST'])
def brands(request):
    filter = request.data['filter']
    subcategory = SubCategory.objects.get(name = filter[1])
    products = Product.objects.filter(subcategory = subcategory)
    brands = Brand.objects.filter(id__in = products)
    serializer = BrandSerializer(brands, many = True)
    return JsonResponse(serializer.data, status = status.HTTP_200_OK, safe = False)


@api_view(['GET',])
def get_trends(request):

    path = os.path.join(settings.BASE_DIR,"data.csv")

    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == 'product name':
                continue
            if row[0] == '':
                break
            product = Product.objects.filter(name = row[0])
            discount = True
            if row[9]==row[14]:
                discount = False
            if len(product)==0:
                category,k =  Category.objects.get_or_create(name = row[11])
                subcategory,k =  SubCategory.objects.get_or_create(name = row[12],category=category.id)
                brand,k =  Brand.objects.get_or_create(name = row[13])
                data = {'category':category.id,'brand':brand.id,'name':row[0],'price':float(row[9]),'discount':discount,
                    'offer_price':float(row[14]), 'stock':row[15],'url':row[16],'hastags':row[8],'buyers':int(row[6])+int(row[7]),
                    'rating':int(row[2]),'searches':int(row[9]),'viewers':int(row[17]),'rank':int(row[18]),'image':None
                    }

                req = urllib.request.Request(url=row[16], headers ={'User-Agent': 'Mozilla / 5.0 (X11 Linux x86_64) AppleWebKit / 537.36 (KHTML, like Gecko) Chrome / 52.0.2743.116 Safari / 537.36 PostmanRuntime/7.29.0'})
                response = urllib.request.urlopen(req)
                html_doc = response.read()
                soup = BeautifulSoup(html_doc, 'html.parser')
                json_object = soup.find(property='twitter:image')
                image_url = json_object.attrs['content']
                if category != 'Mobile' or 'Travel':
                    data['subcategory']=subcategory.id
                serializer = ProductSerializer(data=data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                name = urlparse(image_url).path.split('/')[-1]
                img_temp = NamedTemporaryFile()
                req = urllib.request.Request(url = image_url, headers= {'User-Agent': 'Mozilla / 5.0 (X11 Linux x86_64) AppleWebKit / 537.36 (KHTML, like Gecko) Chrome / 52.0.2743.116 Safari / 537.36 PostmanRuntime/7.29.0'})
                img_temp.write(urllib.request.urlopen(req).read())
                img_temp.flush()
                recipe = Product.objects.get(name = row[0])
                recipe.image.save(row[0], File(img_temp))
                recipe.save()
    content = {"detail":"Members Verified"}
    return JsonResponse(content, safe = False)