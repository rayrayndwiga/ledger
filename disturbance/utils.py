import re
from preserialize.serialize import serialize
from ledger.accounts.models import EmailUser, Document
import traceback

def create_data_from_form(schema, post_data, file_data, post_data_index=None,special_fields=[]):
    data = {} 
    special_fields_list = []
    special_fields_search = SpecialFieldsSearch(special_fields)
    try:
        for item in schema:
            data.update(_create_data_from_item(item, post_data, file_data, 0, ''))
            special_fields_search.extract_special_fields(item, post_data, file_data, 0, '')
        special_fields_list = special_fields_search.special_fields
    except:
        traceback.print_exc()
    return [data],special_fields_list

def extract_assessor_data(item,post_data):
    values = []
    res = {
        'name': item,
        'assessor': '',
        'referrals':[]
    }
    for k in post_data:
        if re.match(item,k):
            values.append({k:post_data[k]})
    if values:
        for v in values:
            for k,v in v.items():
                parts = k.split('{}-'.format(item))
                if len(parts) > 1:
                    # split parts to see if referall
                    ref_parts = parts[1].split('Referral-')
                    if len(ref_parts) > 1:
                        # Referrals
                        res['referrals'].append({
                            'value':v,
                            'email':ref_parts[1],
                            'full_name': EmailUser.objects.get(email=ref_parts[1]).get_full_name()
                        })
                    else:
                        # Assessor
                        res['assessor'] = v

    return res

def _extend_item_name(name, suffix, repetition):
    return '{}{}-{}'.format(name, suffix, repetition)

def _create_data_from_item(item, post_data, file_data, repetition, suffix):
    item_data = {}

    if 'name' in item:
        extended_item_name = item['name']
    else:
        raise Exception('Missing name in item %s' % item['label'])

    if 'children' not in item:
        if item['type'] in ['checkbox' 'declaration']:
            #item_data[item['name']] = post_data[item['name']]
            item_data[item['name']] = extended_item_name in post_data
        elif item['type'] == 'file':
            if extended_item_name in file_data:
                item_data[item['name']] = str(file_data.get(extended_item_name))
            elif extended_item_name + '-existing' in post_data and len(post_data[extended_item_name + '-existing']) > 0:
                item_data[item['name']] = post_data.get(extended_item_name + '-existing')
            else:
                item_data[item['name']] = ''
        else:
            if extended_item_name in post_data:
                if item['type'] == 'multi-select':
                    item_data[item['name']] = post_data.getlist(extended_item_name)
                else:
                    item_data[item['name']] = post_data.get(extended_item_name)
        if item.get('canBeEditedByAssessor'):
            extract_assessor_data(extended_item_name,post_data)
    else:
        if 'repetition' in item:
            item_data = generate_item_data(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
        else:
            item_data = generate_item_data(extended_item_name, item, item_data, post_data, file_data,1,suffix)


    if 'conditions' in item:
        for condition in item['conditions'].keys():
            for child in item['conditions'][condition]:
                item_data.update(_create_data_from_item(child, post_data, file_data, repetition, suffix))

    return item_data

def generate_item_data(item_name,item,item_data,post_data,file_data,repetition,suffix):
    item_data_list = []
    for rep in xrange(0, repetition):
        child_data = {}
        for child_item in item.get('children'):
            child_data.update(_create_data_from_item(child_item, post_data, file_data, 0,
                                                     '{}-{}'.format(suffix, rep)))
        item_data_list.append(child_data)

        item_data[item['name']] = item_data_list
    return item_data

class SpecialFieldsSearch(object):

    def __init__(self,lookable_fields):
        self.lookable_fields = lookable_fields
        self.special_fields = {}

    def extract_special_fields(self,item, post_data, file_data, repetition, suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name'] 
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            for f in self.lookable_fields:
                if item['type'] in ['checkbox' 'declaration']:
                    val = None
                    val = item.get(f,None)
                    if val:
                        item_data[f] = extended_item_name in post_data
                        self.special_fields.update(item_data)
                else:
                    if extended_item_name in post_data:
                        val = None
                        val = item.get(f,None)
                        if val:
                            if item['type'] == 'multi-select':
                                item_data[f] = ','.join(post_data.getlist(extended_item_name))
                            else:
                                item_data[f] = post_data.get(extended_item_name)
                            self.special_fields.update(item_data)
        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
            else:
                item_data = self.generate_item_data_special_field(extended_item_name, item, item_data, post_data, file_data,1,suffix)


        if 'conditions' in item:
            for condition in item['conditions'].keys():
                for child in item['conditions'][condition]:
                    item_data.update(self.extract_special_fields(child, post_data, file_data, repetition, suffix))

        return item_data

    def generate_item_data_special_field(self,item_name,item,item_data,post_data,file_data,repetition,suffix):
        item_data_list = []
        for rep in xrange(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(child_item, post_data, file_data, 0,
                                                         '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data