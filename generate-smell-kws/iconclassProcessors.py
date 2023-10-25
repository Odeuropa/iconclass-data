import glob
import os


class IconclassTxtProcessor:
    def __init__(self, base_dir):
        self._concept_to_name = {}
        txt_filepaths = glob.glob(f'{base_dir}/*.txt')
        for path in txt_filepaths:
            self._concept_to_name.update(self._get_concept_names(path))

    def _get_concept_names(self, path):
        concept_to_name = {}
        with open(path) as f:
            for line in f:
                try:
                    concept, name = line.split('|')
                except ValueError:
                    pass
                concept_to_name[concept] = name.rstrip()
        return concept_to_name

    def concept_name(self,iconclass_code):
        if iconclass_code in self._concept_to_name.keys():
            return self._concept_to_name[iconclass_code]
        else:
            return None
    
    @classmethod
    def for_language(cls,lang):
        base_dir = f'txt/{lang}'
        return cls(base_dir)

class IconclassKWProcessor:
    def __init__(self, lang, out_path='updated_kws'):
        if not os.path.isdir(out_path):
            os.makedirs(out_path)
        self._out_path = out_path
        self._lang = lang
        with open(f'kw/{lang}/kw_{lang}_0_1.txt') as f:
            self._kws_0_1 = f.readlines()
        with open(f'kw/{lang}/kw_{lang}_2_3.txt') as f:
            self._kws_2_3 = f.readlines()
        with open(f'kw/{lang}/kw_{lang}_4.txt') as f:
            self._kws_4 = f.readlines()
        with open(f'kw/{lang}/kw_{lang}_5_6_7_8.txt') as f:
            self._kws_5_6_7_8 = f.readlines()
        with open(f'kw/{lang}/kw_{lang}_9.txt') as f:
            self._kws_9 = f.readlines()    

    @classmethod
    def for_language(cls,lang):
        return cls(lang)


    def add_kw(self, code, kw_string):
        if code.startswith(('0','1')):
            self._kws_0_1.append(kw_string)
        elif code.startswith(('2','3')):
            self._kws_2_3.append(kw_string)
        elif code.startswith('4'):
            self._kws_4.append(kw_string)
        elif code.startswith(('5','6','7','8')):
            self._kws_5_6_7_8.append(kw_string)
        elif code.startswith('9'):
            self._kws_9.append(kw_string)
        else:
            raise Exception("Iconclass code needs to start with a digit.")
        
    def write(self):
        with open(f'{self._out_path}/kws_{self._lang}_0_1.txt', 'w') as f:
            f.writelines(sorted(self._kws_0_1, key=lambda l: (l.split('|')[0], l.split('|')[1])))
        with open(f'{self._out_path}/kws_{self._lang}_2_3.txt', 'w') as f:
            f.writelines(sorted(self._kws_2_3, key=lambda l: (l.split('|')[0], l.split('|')[1])))
        with open(f'{self._out_path}/kws_{self._lang}_4.txt', 'w') as f:
            f.writelines(sorted(self._kws_4, key=lambda l: (l.split('|')[0], l.split('|')[1])))
        with open(f'{self._out_path}/kws_{self._lang}_5_6_7_8.txt', 'w') as f:
            f.writelines(sorted(self._kws_5_6_7_8, key=lambda l: (l.split('|')[0], l.split('|')[1])))
        with open(f'{self._out_path}/kws_{self._lang}_9.txt', 'w') as f:
            f.writelines(sorted(self._kws_9, key=lambda l: (l.split('|')[0], l.split('|')[1])))    

class IconclassNotationProcessor:
    def __init__(self, notations_pth):
        with open(notations_pth) as f:
            self._concept_lines = f.readlines()
        
    def add_reference(self, from_code, to_code):
        try:
            concept_start_idx = self._concept_lines.index(f'N {from_code}\n') 
        except ValueError as ve:
            print(ve)
            return
        r_array = False
        for i,line in enumerate(self._concept_lines[concept_start_idx:]):
            if line.startswith('R'):
                r_array = True
                reference_code = line.split(' ')[-1]
                if reference_code > to_code:
                    insert_idx = i + concept_start_idx
                    # replace R in current line with ;
                    self._concept_lines[i+concept_start_idx] = f'; {reference_code}\n'
                    # insert new reference before current reference with R
                    self._concept_lines.insert(insert_idx, f'R {to_code}\n')
                    return
            if r_array and line.startswith(';'):
                reference_code = line.split(' ')[-1]
                if reference_code > to_code:
                    insert_idx = i + concept_start_idx
                    self._concept_lines.insert(insert_idx, f'; {to_code}\n')
                    return
            if line == '$\n':
                insert_idx = i + concept_start_idx
                if r_array:
                    self._concept_lines.insert(insert_idx, f'; {to_code}\n')
                else:
                    self._concept_lines.insert(insert_idx, f'R {to_code}\n')
                return


    def write(self, target_pth):
        with open(target_pth, 'w') as f:
            f.writelines(self._concept_lines)
            

if __name__ == '__main__':
    prc = IconclassNotationProcessor('notations.txt')
    prc.add_reference('11A11','11D')
    prc.add_reference('0','41')
    prc.add_reference('0','52')
    prc.write('test.txt')


    print('a')
    