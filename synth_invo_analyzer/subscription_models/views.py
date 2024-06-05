from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from authentication.permissions import IsSystemAdmin
from .models import SubscriptionModel, SubscriptionModelFeatures
from authentication.models import SystemAdmin
from .serializers import SubscriptionModelSerializer, SubscriptionModelFeaturesSerializer
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_KEY")

@api_view(['POST'])
@permission_classes([IsSystemAdmin])
def createSubscriptionModel(request):
    admin_id = request.data.get('user_id')
    print(admin_id)
    model_name = request.data.get('model_name')
    unit_amount = request.data.get('unit_amount')
    interval = request.data.get('interval', 'month')  
    currency = request.data.get('currency', 'usd')
    user = SystemAdmin.objects.get(admin_id = admin_id )


    if SubscriptionModel.objects.filter(model_name=model_name).exists():
        return Response(f"Product with the name '{model_name}' already exists.", status=409)  
    try:
        product = stripe.Product.create(
            name=model_name,
            default_price_data={
                "unit_amount": unit_amount * 100,  
                "currency": currency,
                "recurring": {"interval": interval},
            },
            expand=["default_price"],
        )

        
        try:
                sub_model = SubscriptionModel(
                stripe_id=product.id,
                price_id=product.default_price.id,
                model_name=model_name,
                model_price=unit_amount,
                billing_period=interval.capitalize(),  
                created_by=user,
                last_modified_by= user
                )
                sub_model.save()

                return Response("Success", status=201)
        except Exception as e:
            print(e)
            stripe.Product.modify(
                        product.id,
                        active=False  
                    )
            return Response("Database saving failed", status=400)

    except stripe.error.StripeError as e:
        error_message = str(e)
        print("Stripe Error:", error_message)
        return Response("Stripe Error: " + error_message, status=500)

    except Exception as e:
        error_message = "An error occurred while creating the subscription model."
        print("Error:", error_message, e)
        return Response("Internal Server Error: " + error_message, status=500)



@api_view(["POST"])
@permission_classes([IsSystemAdmin])
def modifyProduct(request):
    if not request.user.is_system_admin:
        return Response("You don't have permission to perform this action.", status=403)

    try:
        product_id = request.data['product_id']
        new_name = request.data['model_name']

        updated_product = stripe.Product.modify(
            product_id,
            name=new_name,
        )

        subscription_models = SubscriptionModel.objects.filter(stripe_id=product_id)

        for subscription_model in subscription_models:
            subscription_model.model_name = new_name
            subscription_model.last_modified_by = request.user
            subscription_model.save()

        return Response("Product Updated Successfully", status=200)
    except stripe.error.InvalidRequestError as e:
        return Response("No such product: {}".format(product_id), status=404)
    except Exception as e:
        print(e)
        return Response("Error Updating Product", status=500)


@api_view(["POST"])
@permission_classes([IsSystemAdmin])
def archiveProduct(request):
    if not request.user.is_system_admin:
        return Response("You don't have permission to perform this action.", status=403)

    try:
        product_id = request.data['product_id']

        stripe.Product.modify(
            str(product_id),
            active=False,
        )
        SubscriptionModel.objects.filter(stripe_id=product_id).delete()

        return Response("Product archived successfully.", status=200)
    except stripe.error.StripeError as e:
        return Response(f"Error: {e}", status=500)


@api_view(["GET"])
def getSubscriptionModels(request):
    try:
        models = SubscriptionModel.objects.all()
        serializer = SubscriptionModelSerializer(models, many=True)
        return Response(serializer.data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=404)

@api_view(['POST'])
def create_feature(request):
    model_id = request.data.get('model')
    feature_name = request.data.get('feature')
    
    if SubscriptionModelFeatures.objects.filter(model=model_id, feature=feature_name).exists():
        return Response({"error": "Feature already exists for this model."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = SubscriptionModelFeaturesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def modify_feature(request, pk):
    try:
        feature = SubscriptionModelFeatures.objects.get(pk=pk)
        feature.feature = request.data.get('feature')
        feature.save()
        return Response(status=204)
    except SubscriptionModelFeatures.DoesNotExist:
        return Response(status=404)
    
    

@api_view(['DELETE'])
def remove_feature(request, pk):
    try:
        feature = SubscriptionModelFeatures.objects.get(pk=pk)
    except SubscriptionModelFeatures.DoesNotExist:
        return Response(status=404)

    feature.delete()
    return Response(status=204)

@api_view(['GET'])
def get_features(request, model_id):
    try:
        features = SubscriptionModelFeatures.objects.filter(model=model_id)
        serializer = SubscriptionModelFeaturesSerializer(features, many=True)
        return Response(serializer.data)
    except SubscriptionModelFeatures.DoesNotExist:
        return Response(status=404)
