class Grammar:
    def __init__(self, vn, vt, start_variable, productions):
        self.vn = vn.copy()  # Non-terminal symbols
        self.vt = vt.copy()  # Terminal symbols
        self.start_variable = start_variable
        self.productions = {k: v.copy() for k, v in productions.items()}  # Deep copy of productions
    
    def to_chomsky_normal_form(self):
        new_vn = self.vn.copy()
        new_vt = self.vt.copy()
        new_start = self.start_variable
        new_productions = {k: v.copy() for k, v in self.productions.items()}
        
        print("Original Grammar:")
        self.print_grammar()
        
        need_new_start = False
        
        for productions_list in self.productions.values():
            for production in productions_list:
                if self.start_variable in production:
                    need_new_start = True
                    break
        
        if self.start_variable in self.productions and "ε" in self.productions[self.start_variable]:
            need_new_start = True
        
        original_start = self.start_variable
        if need_new_start:
            new_start = "S0"
            while new_start in new_vn:
                new_start = new_start + "0"
            
            new_vn.append(new_start)
            new_productions[new_start] = [original_start]
            print("\nStep 1: Added new start symbol:", new_start)
        
        self._eliminate_epsilon_productions(new_vn, new_productions)
        
        self._eliminate_unit_productions(new_vn, new_productions)
        
        self._eliminate_inaccessible_symbols(new_vn, new_vt, new_start, new_productions)
        
        self._eliminate_non_productive_symbols(new_vn, new_vt, new_productions)
        
        terminal_to_non_terminal = {}
        terminal_var_counter = 1
        
        for non_terminal in list(new_productions.keys()):
            productions_list = new_productions[non_terminal]
            new_production_list = []
            
            for production in productions_list:
                if len(production) > 1:
                    new_production = ""
                    
                    for i in range(len(production)):
                        symbol = production[i]
                        
                        if symbol in new_vt:
                            if symbol not in terminal_to_non_terminal:
                                new_non_terminal = f"T{terminal_var_counter}"
                                while new_non_terminal in new_vn:
                                    terminal_var_counter += 1
                                    new_non_terminal = f"T{terminal_var_counter}"
                                
                                new_vn.append(new_non_terminal)
                                terminal_to_non_terminal[symbol] = new_non_terminal
                                new_productions[new_non_terminal] = [symbol]
                                terminal_var_counter += 1
                            
                            new_production += terminal_to_non_terminal[symbol]
                        else:
                            new_production += symbol
                    
                    new_production_list.append(new_production)
                else:
                    new_production_list.append(production)
            
            new_productions[non_terminal] = new_production_list
        
        final_productions = {k: v.copy() for k, v in new_productions.items()}
        var_counter = 1
        
        for non_terminal in list(final_productions.keys()):
            productions_list = final_productions[non_terminal]
            new_productions_list = []
            
            for production in productions_list:
                if len(production) > 2:
                    current_nt = non_terminal
                    for i in range(len(production) - 2):
                        next_nt = f"V{var_counter}"
                        while next_nt in new_vn:
                            var_counter += 1
                            next_nt = f"V{var_counter}"
                        
                        new_vn.append(next_nt)
                        
                        if i == 0:
                            new_productions_list.append(production[0] + next_nt)
                        else:
                            if current_nt not in final_productions:
                                final_productions[current_nt] = []
                            final_productions[current_nt].append(production[i] + next_nt)
                        
                        current_nt = next_nt
                        var_counter += 1
                    
                    if current_nt not in final_productions:
                        final_productions[current_nt] = []
                    final_productions[current_nt].append(production[-2:])
                else:
                    new_productions_list.append(production)
            
            if new_productions_list:
                final_productions[non_terminal] = new_productions_list
        
        cnf_grammar = Grammar(new_vn, new_vt, new_start, final_productions)
        return cnf_grammar
    
    def _eliminate_epsilon_productions(self, vn, productions):
        print("\nStep 2: Eliminating ε productions")
        
        nullable = set()
        changed = True
        
        while changed:
            changed = False
            for non_terminal in vn:
                if non_terminal not in nullable and non_terminal in productions:
                    non_terminal_productions = productions[non_terminal]
                    
                    if "ε" in non_terminal_productions:
                        nullable.add(non_terminal)
                        changed = True
                    else:
                        for production in non_terminal_productions:
                            all_nullable = True
                            for i in range(len(production)):
                                symbol = production[i]
                                if symbol not in nullable:
                                    all_nullable = False
                                    break
                            
                            if all_nullable and production:
                                nullable.add(non_terminal)
                                changed = True
                                break
        
        print(f"Nullable symbols: {nullable}")
        
        for non_terminal in vn:
            if non_terminal in productions:
                non_terminal_productions = productions[non_terminal]
                if "ε" in non_terminal_productions:
                    non_terminal_productions.remove("ε")
                
                new_productions = []
                for production in non_terminal_productions:
                    self._add_all_combinations(production, nullable, new_productions)
                
                non_terminal_productions.extend(new_productions)
                productions[non_terminal] = list(set(non_terminal_productions))
    
    def _add_all_combinations(self, production, nullable, result):
        nullable_positions = []
        
        for i in range(len(production)):
            symbol = production[i]
            if symbol in nullable:
                nullable_positions.append(i)
        
        if nullable_positions:
            combinations = 1 << len(nullable_positions)
            
            for i in range(1, combinations):
                new_production = list(production)
                offset = 0
                
                for j in range(len(nullable_positions)):
                    if (i & (1 << j)) != 0:
                        pos = nullable_positions[j] - offset
                        new_production.pop(pos)
                        offset += 1
                
                new_prod_str = ''.join(new_production)
                if new_prod_str and new_prod_str not in result:
                    result.append(new_prod_str)
    
    def _eliminate_unit_productions(self, vn, productions):
        print("\nStep 3: Eliminating unit productions")
        
        unit_pairs = {}
        
        for non_terminal in vn:
            pairs = set()
            pairs.add(non_terminal)
            unit_pairs[non_terminal] = pairs
        
        changed = True
        while changed:
            changed = False
            
            for a in vn:
                a_pairs = set(unit_pairs[a])
                
                for b in list(a_pairs):
                    if b in productions:
                        b_productions = productions[b]
                        
                        for production in b_productions:
                            if len(production) == 1 and production in vn:
                                c = production
                                if c not in unit_pairs[a]:
                                    unit_pairs[a].add(c)
                                    changed = True
        
        print(f"Unit pairs: {unit_pairs}")
        
        new_productions = {}
        
        for non_terminal in vn:
            non_unit_productions = []
            
            if non_terminal in unit_pairs:
                for unit_non_terminal in unit_pairs[non_terminal]:
                    if unit_non_terminal in productions:
                        for production in productions[unit_non_terminal]:
                            if not (len(production) == 1 and production in vn):
                                non_unit_productions.append(production)
            
            if non_unit_productions:
                new_productions[non_terminal] = list(set(non_unit_productions))
            else:
                new_productions[non_terminal] = []
        
        productions.clear()
        productions.update(new_productions)
    
    def _eliminate_inaccessible_symbols(self, vn, vt, start_variable, productions):
        print("\nStep 4: Eliminating inaccessible symbols")
        
        accessible = set()
        queue = []
        
        accessible.add(start_variable)
        queue.append(start_variable)
        
        while queue:
            current = queue.pop(0)
            
            if current in productions:
                for production in productions[current]:
                    for i in range(len(production)):
                        symbol = production[i]
                        
                        if symbol in vn and symbol not in accessible:
                            accessible.add(symbol)
                            queue.append(symbol)
                        elif symbol in vt:
                            accessible.add(symbol)
        
        print(f"Accessible symbols: {accessible}")
        
        inaccessible_nt = []
        for non_terminal in list(vn):
            if non_terminal not in accessible:
                inaccessible_nt.append(non_terminal)
                if non_terminal in productions:
                    del productions[non_terminal]
        
        for nt in inaccessible_nt:
            vn.remove(nt)
        
        inaccessible_t = []
        for terminal in list(vt):
            if terminal not in accessible:
                inaccessible_t.append(terminal)
        
        for t in inaccessible_t:
            vt.remove(t)
    
    def _eliminate_non_productive_symbols(self, vn, vt, productions):
        print("\nStep 5: Eliminating non-productive symbols")
        
        productive = set(vt)
        changed = True
        
        while changed:
            changed = False
            for non_terminal in list(vn):
                if non_terminal not in productive and non_terminal in productions:
                    non_term_productions = productions[non_terminal]
                    
                    for production in non_term_productions:
                        all_productive = True
                        
                        for i in range(len(production)):
                            symbol = production[i]
                            if symbol not in productive:
                                all_productive = False
                                break
                        
                        if all_productive:
                            productive.add(non_terminal)
                            changed = True
                            break
        
        print(f"Productive symbols: {productive}")
        
        non_productive_nt = []
        for non_terminal in list(vn):
            if non_terminal not in productive:
                non_productive_nt.append(non_terminal)
                if non_terminal in productions:
                    del productions[non_terminal]
        
        for nt in non_productive_nt:
            vn.remove(nt)
        
        for non_terminal in list(productions.keys()):
            production_list = productions[non_terminal]
            to_remove = []
            
            for production in production_list:
                for i in range(len(production)):
                    symbol = production[i]
                    if symbol not in productive:
                        to_remove.append(production)
                        break
            
            for prod in to_remove:
                production_list.remove(prod)
            
            if not production_list:
                del productions[non_terminal]
                if non_terminal in vn:
                    vn.remove(non_terminal)
    
    def print_grammar(self):
        print("Grammar {")
        print(f"  VN = {self.vn}")
        print(f"  VT = {self.vt}")
        print(f"  S = {self.start_variable}")
        print("  P = {")
        for nt, productions_list in self.productions.items():
            print(f"    {nt} → {' | '.join(productions_list)}")
        print("  }")
        print("}")


def main():
    vn = ["S", "A", "B", "C", "D"]
    vt = ["a", "b"]
    start_variable = "S"
    
    productions = {
        "S": ["aB", "DA"],
        "A": ["a", "BD", "bDAB"],
        "B": ["b", "BA"],
        "D": ["ε", "BA"],
        "C": ["BA"]
    }
    
    grammar = Grammar(vn, vt, start_variable, productions)
    
    cnf_grammar = grammar.to_chomsky_normal_form()
    
    print("\nTransformed Grammar in Chomsky Normal Form:")
    cnf_grammar.print_grammar()


if __name__ == "__main__":
    main()