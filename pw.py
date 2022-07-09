
import zymkey
import logging
import time

#multi-sig
_2of3or2of2 = "_2of3or2of2"
_3of5or2of3 = "_3of5or2of3"
_5of9or3of4 = "_5of9or3of4"
#uni-sig user
_1of2or3of4 = "_1of2or3of4"
_1of2or5of9 = "_1of2or5of9"


print("Enter ceremony generation number.")
generation = input()
print("_2 of 3 and 2 of 2 backup ?")
_2of3 = input()
print("_3 of 5 and 2 of 3 backup ?")
_3of5 = input()
print("_5 of 9 and 3 of 4 backup ?")
_5of9 = input()
print("_1 of 2 or 3 of 4 backup ??")
_1or3of4 = input()
print("_1 of 2 or 5 of 9 backup?")
_1or5of9 = input()


order = [

    {_2of3or2of2:_2of3},
    {_3of5or2of3:_3of5},
    {_5of9or3of4:_5of9},
    {_1of2or3of4:_1or3of4},
    {_1of2or5of9:_1or5of9},
]

def generate_pw(generation,order):
    """
    -submit order to key generation algorithm using zymkey module
    and HSM 6 of Zymbit.
    
    -create wallet constituted of 2 groups: the owners and the backup.
    Each group can have different number of members able to recover master seed.
    
    """
    order_outputs_list = []
    for i in order:
        for product_type,v in i.items():
            for w in range(int(v)):
                
                if product_type == _2of3or2of2:
                    
                    #multi-sig params for _2of3
                    group_member=3
                    member_threshold=2
    
                    backup_group_member= 2
                    backup_member_threshold= 2          
                                    
                
                elif product_type == _3of5or2of3:   
                    
                    #multi-sig params for _3of5or2of3
                    group_member=5
                    member_threshold=3
    
                    backup_group_member= 3
                    backup_member_threshold= 2  
                        
                elif product_type == _5of9or3of4:
                    
                    #multi-sig params for _5of9or3of4
                    group_member=9
                    member_threshold=5
    
                    backup_group_member= 4
                    backup_member_threshold= 3  
                            
                elif product_type == _1of2or3of4:
                    
                    #multi-sig params for _1or3of4
                    group_member=2
                    member_threshold=1
    
                    backup_group_member= 4
                    backup_member_threshold= 3                  
                    
                elif product_type == _1of2or5of9:
                                        
                    #multi-sig params for _1or5of9
                    group_member=2
                    member_threshold=1
    
                    backup_group_member= 9
                    backup_member_threshold= 5  
                                        
    
                #multi-sig params with 2 groups: backup + owner
                group_count = 2
                group_threshold = 1
                group_member_count_list = []    
                backup_count = 1
                backup_counter = 0
                
                for i in range(group_count):
                    if backup_counter >= backup_count:
                                    
                        group_id = f"group_{i}"                                 
                        group_member_count_list.append(
                            {group_id:[
                                {"group_member":group_member},
                                {"member_threshold":member_threshold}
                            ]},
                        )
                    else:
                                
                        backup_id = f"backup_{i}"                           
                        group_member_count_list.append(
                            {backup_id:[
                                {"group_member":backup_group_member},
                                {"member_threshold":backup_member_threshold}
                            ]}                                                      
                        )               
                    backup_counter += 1
    
                try:
    
                    #set unique wallet name
                    wallet_name = str(generation) + "-" + zymkey.client.get_random(num_bytes=10).hex()  
                    
                    print(f"Start generating a multisig wallet with backup having the id {wallet_name}... \n",group_member_count_list)      
                                    
                    use_slip39_recovery = zymkey.RecoveryStrategySlip39(
                        group_count = group_count, 
                        group_threshold = group_threshold, 
                        iteration_exponent = 0, 
                        variant = "", 
                        passphrase = "" 
                    )
                    #print("Starting slip39 shard generating session...")
                    
                    return_code = zymkey.client.gen_wallet_master_seed(
                        "secp256k1", 
                        "", 
                        wallet_name, 
                        use_slip39_recovery
                    )
                    #print("Done! Return Code:%i" % (return_code))
                    
                    #params for shards
                    counter = 0         
                    groups_shards_list = []
                    
                    #gen shards for groups
                    for i in group_member_count_list:
                    
                        for k,v in i.items():

                            group_member = v[0].get('group_member')
                            member_threshold = v[1].get('member_threshold')
                            #print(group_member, member_threshold)
                            
                            #print("\nSet our first example group configuration..")
                            
                            zymkey.client.set_gen_slip39_group_info(
                                group_index = counter, 
                                member_count = group_member , 
                                member_threshold = member_threshold
                            )
                            
                            counter += 1
                            
                            members_shard_list = []
                            
                            for j in range(group_member):
                                ret, mnemonic_shard = zymkey.client.add_gen_slip39_member_pwd()
                                members_shard_list.append(mnemonic_shard)
                                #print("Shard #%i , Mnemonic sentence:\n%s" % (j+1, members_shard_list[j]))
                            
                            groups_shards_list.append({k:members_shard_list})
                                
                            if ret >= 0:
                                #verify public key
                                child_slot = zymkey.client.gen_wallet_child_key(ret, 0 , False)
                                child_pub_key = zymkey.client.get_public_key(child_slot)
                                
                                #removing the master key to verify
                                zymkey.client.remove_key(ret)
                                
                                #verify if recovery strategy works
                                
                                #params
                                backup_verified = False
                                group_verified = False                          
                                
                                print(f"Start verifying master seed recovery, removing original master seed and reconstructing it using our multisig with id {wallet_name} ...\n")                          
                                for s in groups_shards_list:
                                    
                                    for k,v in s.items():

                                        #reconstruct secret
                                        return_code = zymkey.client.restore_wallet_master_seed("secp256k1", "", wallet_name, use_slip39_recovery)
            
                                        #get fist index to test against all other seed
                                        #when done, increment to test the rest of
                                        #combinatoric possibilities 
                                        
                                        if k == "backup_0":
                                            num = backup_member_threshold
                                        else:
                                            num = member_threshold
                                                                                                                                                                                                                        
                                        for i in range(num):
                                            
                                            verify_ret = zymkey.client.add_restore_slip39_mnemonic(mnemonic_sentence = v[i])                

                                            if verify_ret >= 0:
                                                
                                                verify_child_slot = zymkey.client.gen_wallet_child_key(verify_ret, 0 , False)
                                                verify_child_pub_key = zymkey.client.get_public_key(verify_child_slot)
                                                
                                                #verify if original pub is the same is reconstructed pub
                                                if verify_child_pub_key == child_pub_key:
                                                    
                                                    if k == "backup_0":
                                                        backup_verified = True
                                                    else:
                                                        group_verified = True
                                                                                                
                                                    print(f"DONE! Verified {k} reconstitution with id {wallet_name} . \n")
                                                    
                                                    if group_verified == True and backup_verified == True:
                                                        
                                                        order_outputs_list.append({wallet_name:{product_type:groups_shards_list}})
                                                        
                                                    pass
                                                    
                                                else:
                                                    
                                                    print("ERROR. No Verified reconstitution \n")
                                                    raise logging.exception("message")
                                                
                                                zymkey.client.remove_key(verify_ret)                                            
                                            
                    zymkey.client.cancel_slip39_session()
                    
                except Exception as e:
                    logging.exception("message")
                    
                    zymkey.client.cancel_slip39_session()
    
    print("order_outputs_list",order_outputs_list)


generate_pw(generation,order)   



#
#
#from fpdf import FPDF
#
#
#class PDF(FPDF):
#    pass # nothing happens when it is executed.
#
#    def imagex(self):
#        self.set_xy(6.0,6.0)
#        self.image(sctplt,  link='', type='', w=1586/80, h=1920/80)
#        self.set_xy(183.0,6.0)
#        self.image(sctplt2,  link='', type='', w=1586/80, h=1920/80)
#
#    def titles(self):
#        self.set_xy(0.0,0.0)
#        self.set_font('Arial', 'B', 16)
#        self.set_text_color(220, 50, 50)
#        self.cell(w=210.0, h=40.0, align='C', txt="Wallet", border=0)
#
#    def imagex(self):
#        self.set_xy(183.0,6.0)
#        self.image("logo.png",  link='', type='', w=1586/80)
#        # self.image(sctplt2,  link='', type='', w=1586/80, h=1920/80)
#
#    def line_1(self):
#        self.set_xy(0.0,13.0)
#        self.set_font('Arial', 'B', 12)
#        self.set_text_color(12, 50, 50)
#        self.cell(w=210.0, h=40.0, align='C', txt="Your multi-signature wallet enables you to backup your wallet.", border=0)
#
#    def line_2(self):
#        self.set_xy(0.0,19.0)
#        self.set_font('Arial', 'B', 12)
#        self.set_text_color(12, 50, 50)
#        self.cell(w=210.0, h=40.0, align='C', txt="Your multi-signature wallet enables you to backup your wallet.", border=0)
#
#    def line_3(self):
#        self.set_xy(0.0,19.0)
#        self.set_font('Arial', 'B', 12)
#        self.set_text_color(12, 50, 50)
#        self.cell(w=210.0, h=40.0, align='C', txt="Your multi-signature wallet enables you to backup your wallet.", border=0)
#
#
#
#
#
#
#pdf = PDF(orientation='P', unit='mm', format='A4')
#pdf.add_page()
#
#pdf.titles()
#pdf.line_1()
#pdf.line_2()
#pdf.line_3()
#pdf.imagex()
#
#
#pdf.output('test.pdf','F')






 # VERIFY EACH COMBINAISON USING THIS FUNCTION
#                               #verify if recovery strategy works
#                               for s in groups_shards_list:
#                                   
#                                   for k,v in s.items():
#                                       
#                                       #get fist index to test against all other seed
#                                       #when done, increment to test the rest of
#                                       #combinatoric possibilities                                                                                                                                                                                             
#                                       for i in range(group_member):
#                                           
#                                           #get other seed                                                                                                                 
#                                           for t in range(group_member):
#                                               
#                                               #if t is not equals to i, execute script
#                                               #get complementary seed by seting up index
#                                               #to retrieve seeds from groups_shards_list 
#                                               if t > i and t < int(group_member-1):
#                                                   
#                                                   #manage threshold requirements                                      
#                                                   for u in range(member_threshold-1):     
#                                                       
#                                                       #increment to test all combinatorics 
#                                                       #according to positions in groups_shards_list
#                                                       index = t + u
#                                                       
#                                                       if index <= len(v)-1:                                                       
#                                                       
#                                                           #print("i>> ",i,"t>>",t,"index>>",index,"u>>",u,"t>>",t,"list>>",v)
#                                                           
#                                                           #reconstruct secret
#                                                           return_code = zymkey.client.restore_wallet_master_seed("secp256k1", "", wallet_name, use_slip39_recovery)
#                                                           #print("Done! Return Code:%i" % (return_code))                                                      
#                                                           
#                                                           zymkey.client.add_restore_slip39_mnemonic(mnemonic_sentence = v[i])                                                 
#                                                           verify_ret = zymkey.client.add_restore_slip39_mnemonic(mnemonic_sentence = v[index])                
#   
#                                                           if verify_ret >= 0:
#                                                               
#                                                               verify_child_slot = zymkey.client.gen_wallet_child_key(verify_ret, 0 , False)
#                                                               #print("verify - child_slot",verify_child_slot) 
#                                                               verify_child_pub_key = zymkey.client.get_public_key(verify_child_slot)
#                                                               #print("Verify - Child Public Key: %s" % (verify_child_pub_key))                                                            
#                                                               
#                                                               #verify if original pub is the same is reconstructed pub
#                                                               if verify_child_pub_key == child_pub_key:
#                                                                   
#                                                                   print("DONE. Verified reconstitution \n")
#                                                                   pass
#                                                                   
#                                                               else:
#                                                                   
#                                                                   print("ERROR. No Verified reconstitution \n")
#                                                                   raise logging.exception("message")
#                                                               
#                                                               zymkey.client.remove_key(verify_ret)                                                                
                                                                