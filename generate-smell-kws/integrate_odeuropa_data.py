import pandas as pd
from iconclassProcessors import IconclassTxtProcessor, IconclassKWProcessor, IconclassNotationProcessor
from tqdm import tqdm
import os

_OBJECTS_CODE = '31A3331'
_ICONOGRAPHY_CODE = '31A3332'
_SPACES_CODE = '31A3333'

def prepare_df(df):
    if 'ICONCLASS' not in df.columns:
        df = df.rename(columns={'ICONCLASS CODE': 'ICONCLASS'})
    if 'RELATED SCENT' not in df.columns:
        df = df.rename(columns={"RELATED SCENT (see 'art historical scent wheel in google drive' for categories)": "RELATED SCENT"})
    merge_candidates = df[df['ICONCLASS'].notnull()]
    merge_candidates = merge_candidates[merge_candidates['ICONCLASS'].str.match('^([0-9])')]
    merge_candidates = merge_candidates[merge_candidates['RELATED SCENT'].notnull()]
    return merge_candidates

def add_kws(df, txt_processor: IconclassTxtProcessor, kw_processor: IconclassKWProcessor):
    for _, row in tqdm(df.iterrows()):
        code = row["ICONCLASS"]
        scents = row["RELATED SCENT"].split(',')
        name = txt_processor.concept_name(code)
        for scent in scents:
            kw_string = f'{code}|{scent.strip()}{os.linesep}'
            if name is None:
                print(f'{code} not found in txt files.')    
            else:
                kw_processor.add_kw(code, kw_string)

def integrate_kws(lang, iconography_df, objects_df, spaces_df):
    txt_processor = IconclassTxtProcessor.for_language(lang)
    kw_processor = IconclassKWProcessor.for_language(lang)

    # add smell keywords to each concept in odeuropa csvs
    for df in [iconography_df, objects_df, spaces_df]:
        df = prepare_df(df)
        add_kws(df, txt_processor, kw_processor)
    kw_processor.write()

def integrate_cross_references(notations_pth, iconography_df, objects_df, spaces_df):
    # add cross references for concepts in odeuropa csvs
    notations_processor = IconclassNotationProcessor(notations_pth)
    ## objects
    for code in objects_df['ICONCLASS CODE']:
        notations_processor.add_reference(code, _OBJECTS_CODE)
    ## iconography
    for code in iconography_df['ICONCLASS']:
        notations_processor.add_reference(code, _ICONOGRAPHY_CODE)
    ## places
    for code in spaces_df['ICONCLASS CODE']:
        notations_processor.add_reference(code, _SPACES_CODE)
    
    notations_processor.write('odeuropa_notations.txt')


if __name__ == '__main__':
    langs = ['en']

    iconography_df = pd.read_csv('generate-smell-kws/odeuropa-taxonomy/iconography.csv')
    objects_df = pd.read_csv('generate-smell-kws/odeuropa-taxonomy/objects.csv')
    spaces_df = pd.read_csv('generate-smell-kws/odeuropa-taxonomy/spaces.csv')
    

    for lang in langs:
        integrate_kws(lang, iconography_df, objects_df, spaces_df)

    integrate_cross_references('notations.txt', iconography_df, objects_df, spaces_df)
