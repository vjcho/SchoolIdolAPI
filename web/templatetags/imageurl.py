from django import template
from django.conf import settings
from web.utils import chibiimage as _chibiimage
from api.models import LINK_IMAGES, LINK_URLS
from api.raw import raw_information
import os.path
import string
import re

register = template.Library()

def _imageurl(path):
    return '%s%s' % (settings.IMAGES_HOSTING_PATH, path)

@register.simple_tag(takes_context=True)
def imageurl(context, card, image, english_version=False):
    if english_version:
        image = 'english_' + image
    if hasattr(card, image):
        card_image = getattr(card, image)
        if card_image:
            return _imageurl(unicode(card_image))
    return 'http://i.schoolido.lu/static/default-' + card.attribute + '.png'

@register.filter
def account_is_world(account):
    return account.language != 'JP'

@register.simple_tag(takes_context=True)
def cleanurl(context, card, idolized, small=True):
    if idolized:
        if card.clean_ur_idolized:
            if small:
                return _imageurl(str(card.clean_ur_idolized).replace('/cards/ur_pairs/', '/cards/ur_pairs/small_'))
            else:
                return _imageurl(str(card.clean_ur_idolized))
        return _imageurl(str(card.card_idolized_image))
    else:
        if card.clean_ur:
            if small:
                return _imageurl(str(card.clean_ur).replace('/cards/ur_pairs/', '/cards/ur_pairs/small_'))
            else:
                return _imageurl(str(card.clean_ur))
        return _imageurl(str(card.card_image))

@register.simple_tag()
def cardrawurl(card_id, idol_name, image_type, english_version=False):
    prefix = 'c/'
    if english_version:
        prefix = 'cards/'
    if image_type == 'round_card_image':
        return _imageurl(prefix + str(card_id) + 'Round' + idol_name + '.png')
    elif image_type == 'round_card_idolized_image':
        return _imageurl(prefix + str(card_id) + 'RoundIdolized' + idol_name + '.png')
    elif image_type == 'card_image':
        return _imageurl(prefix + str(card_id) + idol_name + '.png')
    elif image_type == 'card_image':
        return _imageurl(prefix + str(card_id) + 'idolized' + idol_name + '.png')
    return 'http://i.schoolido.lu/static/empty.png'

@register.simple_tag()
def cardidolizedimageurl(card, idolized, english_version=False):
    prefix = 'english_' if english_version else ''
    if card.is_special or card.is_promo:
        idolized = True
    if idolized:
        if getattr(card, prefix + 'round_card_idolized_image'):
            return _imageurl(getattr(card, prefix + 'round_card_idolized_image'))
        if getattr(card, prefix + 'card_idolized_image'):
            return _imageurl(getattr(card, prefix + 'card_idolized_image'))
        return 'http://i.schoolido.lu/static/default-' + card.attribute + '.png'
    if getattr(card, prefix + 'round_card_image'):
        return _imageurl(getattr(card, prefix + 'round_card_image'))
    if getattr(card, prefix + 'card_image'):
        return _imageurl(getattr(card, prefix + 'card_image'))
    return 'http://i.schoolido.lu/static/default-' + card.attribute + '.png'

@register.simple_tag(takes_context=True)
def ownedcardimageurl(context, ownedcard, card=None, english_version=False):
    if not ownedcard:
        return 'http://i.schoolido.lu/static/default-All.png'
    if not card:
        card = ownedcard.card
    idolized = True if card.is_special or card.is_promo else ownedcard.idolized
    return cardidolizedimageurl(card, idolized, english_version=english_version)

@register.simple_tag(takes_context=True)
def eventimageurl(context, event, english=False):
    if english and event.english_image:
        return u'%s%s' % (settings.IMAGES_HOSTING_PATH, unicode(event.english_image))
    if event.image:
        return u'%s%s' % (settings.IMAGES_HOSTING_PATH, unicode(event.image))
    return 'http://i.schoolido.lu/static/default_event.png'

@register.simple_tag(takes_context=True)
def songimageurl(context, song):
    if song.image:
        if settings.DEBUG:
            song.image = unicode(song.image).replace('web/', '')
        return u'%s%s' % (settings.IMAGES_HOSTING_PATH, unicode(song.image))
    return 'http://i.schoolido.lu/static/defaultsong.png'

def userimage(image):
    return u'%s%s' % (settings.IMAGES_HOSTING_PATH, unicode(image))

@register.simple_tag(takes_context=True)
def standimage(context, idol, number):
    if idol is not None:
        if idol.main_unit == 'Aqours':
            if number == 5:
                return raw_information[idol.name]['image'].replace('Transparent', 'idolizedTransparent')
            return raw_information[idol.name]['image']
        m = re.search(r'[^0-9]+(?P<number>[0-9]+)[.]html$', idol.official_url)
        member_number = m.group('number')
        return 'http://www.lovelive-anime.jp/otonokizaka/img/member/member' + member_number + '_0'+ str(number) + '.png'
    return ''

@register.simple_tag(takes_context=True)
def idolimage(context, name):
    filename = name.replace(' ', '_').replace('\'', '-')
    return filename

def linkimage(link):
    return LINK_IMAGES.get(link['type'], None)

def linkurl(link):
    return LINK_URLS[link['type']].format(link['value'])

@register.simple_tag(takes_context=True)
def chibiimage(context, idol, small=True, force_first=False, force_artist=False):
    return _chibiimage(idol, small, force_first=force_first, force_artist=force_artist)

@register.filter
def chibioriginal(link):
    return link.replace('/chibi/', '/chibi/original-')

@register.filter
def accountattribute(account):
    if account.fake:
        return 'default'
    if account.center_id:
        return account.center_card_attribute
    return 'All'

register.filter('userimage', userimage)
register.filter('linkimage', linkimage)
register.filter('linkurl', linkurl)
