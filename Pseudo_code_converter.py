







def Pseudo_Converter(Pseudo_code,input1=0,input2=0,input3=0): #if you don't need the other inputs put them as zeros

   #Our list of pseudo instrctions.
   Pseudo_inserction_array = ['la', 'call', 'ret', 'mv', 'bgtz', 'beqz','ble', 'blez', 'li', 'j'
                              ,'nop','not','neg','negw','sext','seqz','snez','sltz','sgtz'


                              ]



   #Our output objects

   return_obj=''
   Is_this_instruction_included=False



#check if the entry is valid the inputs are not going to be numbers but strings change the checking portion

# 1- input check 2-la and call make sure they work correctly 3-make the call and la returns as 'instruction input input' then 'instruction input input'
# 4 add the other instructions 5-make the sawp instruction

   # what is done: added all the basic instructions (but the ones woth two lines)
   # waht is still to be done gola 1 and 5

   if ( (type(Pseudo_code)) == str and (type(input1))==int and (type(input2)==int) and (type(input3)==int)): #all the inputs are going to be strings i could check by converting str to int

      #check if the Pcode is registered
      for i in range(len(Pseudo_inserction_array)):
         if Pseudo_inserction_array[i] is Pseudo_code:


            Is_this_instruction_included=True
            print('This instruction is included')

      if not Is_this_instruction_included:
         print('This instruction in not included in this method')
         return




# this section for instructions with 2 lines output

      # IMPORTANT I might need to add a method to make sign extensiones beacuse when I have an input of 32-bits as an arg for an instruction the user should be able to use less than 32
      # and I should do the extension to make the input a 32bits input.



      if Pseudo_code == 'la': # this is the la instruction load adress

         symbol= str(input1)
         # check if the input is valid, the symbol size must be 32
         if len(symbol)==32: #this shouldn't be 32 if it not then u should sign extended it so it becomes 32
            print('valid symbol of', len(symbol))
            return ('auipc '+input1+''+symbol[12:31],'addi '+input1+''+input1+''+symbol[0:11])


         else:
            print('none valid entrey of symbol. symbol size must be 32 bits')



      if Pseudo_code == 'call': #call instruction call faraway subroutine
         offset = str(input1)

         # check if the input is valid, the offset size must be 32
         if len(offset) == 32:
            print('valid offset of',len(offset))
            upperoffset=offset[12:31]
            loweroffset=offset[0:11]
            print(loweroffset)

            return ('auipc x1 '+ offset[12:31], 'jalr x1 x1 '+ offset[0:11])


         else:
            print('none valid entrey of offset. offset size must be 32 bits')


      if Pseudo_code == 'la':  # this is the la instruction load adress

         symbol = str(input1)
         # check if the input is valid, the symbol size must be 32
         if len(symbol) == 32:  # this shouldn't be 32 if it not then u should sign extended it so it becomes 32
            print('valid symbol of', len(symbol))
            return ('auipc ' + input1 + '' + symbol[12:31], 'addi ' + input1 + '' + input1 + '' + symbol[0:11])


         else:
            print('none valid entrey of symbol. symbol size must be 32 bits')







#-------------------------------------------------------------------------------------------------------------------#

      if Pseudo_code == 'ret': # ret instruction
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = ''
         return ('jalr x0, x1, 0')

      if Pseudo_code == 'mv': #mv copy register instruction
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'addi ' + string_buffer1 +', '+string_buffer2+', 0'+ "'"
         return output_str



      if Pseudo_code == 'li': # li load immediate input1 is the rd and input is the immediate
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'addi ' +string_buffer1+', '+string_buffer1 +', '+string_buffer2+"'"

         return output_str

      if Pseudo_code == 'j':#j
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str= "'"+'jal x0, '+string_buffer1+"'"

         return output_str

      #-------------------------------------------------------------------------#

      #'nop','not','neg','negw','sext','seqz','snez','sltz','sgtz'

      if Pseudo_code == 'nop':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'"+'addi x0, x0, 0'+"'"

         return output_str

      if Pseudo_code == 'not':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str =  "'" + 'xori '+ string_buffer1 +', '+string_buffer2+', '+'-1'+"'"

         return output_str

      if Pseudo_code == 'neg':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'"+'sub '+ string_buffer1 +', x0, '+string_buffer2+"'"

         return output_str

      if Pseudo_code == 'negw':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" +'subw '+ string_buffer1 +', x0, '+string_buffer2+"'"

         return output_str

      if Pseudo_code == 'sext':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'addiw ' + string_buffer1 +', '+string_buffer2+', '+'0'+"'"

         return output_str

      if Pseudo_code == 'seqz':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'sltiu '+ string_buffer1 +', '+string_buffer2+', '+'1'+"'"

         return output_str

      if Pseudo_code == 'snez':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'sltu ' + string_buffer1 +', x0, '+string_buffer2+"'"

         return output_str

      if Pseudo_code == 'sltz':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'slt ' + string_buffer1 +', '+string_buffer2+', '+'x0'+ "'"

         return output_str

      if Pseudo_code == 'sgtz':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'slt ' + string_buffer1 +', x0, '+string_buffer2+"'"

         return output_str

      #-------------------------------------------------------------------------#

      # Branching codes
      if Pseudo_code == 'bgtz': #bgtz branch if zero
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'blt x0,' + string_buffer1 +', '+string_buffer2+ "'"
         return output_str

      if Pseudo_code == 'beqz': #beqz branch if zero
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'beq ' + string_buffer1 +', x0, '+string_buffer2 + "'"
         return output_str

      if Pseudo_code == 'ble':  # ble branch if <=
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'bge ' +string_buffer2+', '+string_buffer1+', '+string_buffer3 + "'"
         return output_str

      if Pseudo_code == 'blez': # blez branch if <= zero
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'bge x0, ' +string_buffer1+', '+string_buffer2 + "'"
         return output_str

      #----------------------------------------------------------------------------------------#

      # bnez bgez bltz bgt bgtu bleu

      if Pseudo_code == 'bnez':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'bne ' + string_buffer1 +', x0, '+string_buffer2+"'"

         return output_str


      if Pseudo_code == 'bgez':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'bge ' + string_buffer1 +', x0, '+string_buffer2+"'"

         return output_str


      if Pseudo_code == 'bltz':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'slt ' + string_buffer1 +', x0, '+string_buffer2+"'"

         return output_str


      if Pseudo_code == 'bgt':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'blt '+string_buffer2+', '+string_buffer1+', '+string_buffer3 + "'"

         return output_str


      if Pseudo_code == 'bgtu':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'bltu '+string_buffer2+', '+string_buffer1+', '+string_buffer3 + "'"

         return output_str


      if Pseudo_code == 'bleu':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'bgeu '+string_buffer2+', '+string_buffer1+', '+string_buffer3 + "'"

         return output_str


   # ------------------------------------------------------------------- #

   # jal jr jalr tail

      if Pseudo_code == 'jal':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'jal x1, '+string_buffer1+"'"

         return output_str


      if Pseudo_code == 'jr':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'jal x0, '+string_buffer1+', '+'0'+"'"

         return output_str


      if Pseudo_code == 'tail':
         string_buffer1 = str(input1)
         string_buffer2 = str(input2)
         string_buffer3 = str(input3)
         output_str = "'" + 'bgeu '+string_buffer2+', '+string_buffer1+', '+string_buffer3 + "'"

         return output_str








   else:
      output = "False entry"
      print(output)
      return("FALSE ENTRY")


number=12345678901234567890123456789012
number_to_string= str(12345678901234567890123456789012)

print(Pseudo_Converter('j',0,0,0))


n=121212
t= type(n)
print(t)